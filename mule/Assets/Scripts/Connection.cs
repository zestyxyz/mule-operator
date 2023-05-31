using UnityEngine;
using Unity.WebRTC;
using System.Text;
using SocketIOClient;
using SocketIOClient.Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public class Connection : MonoBehaviour
{
	[SerializeField] private string serverUrl = "http://192.168.2.11:9000";
	[SerializeField] string roomName = "test";
	
	private SocketIOUnity socket;
	
	private RTCPeerConnection peerConnection;
	private RTCDataChannel dataChannel;
	private DelegateOnDataChannel delegateOnDataChannel;
	private MediaStream stream;
	
	private bool isRemoteDescriptionSet = false;
	private bool isLocalDescriptionSet = false;
	private bool isIceCandidateSet = false;
	
	private GameObject screen;
	// Start is called before the first frame update
	void Start()
	{
		screen = GameObject.Find("screen");
		delegateOnDataChannel 
		= delegate (RTCDataChannel channel)
		{
			dataChannel = channel;
			dataChannel.OnOpen += OnDataChannelOpen;
			dataChannel.OnMessage += OnDataChannelMessage;
		};
		
		socket = new SocketIOUnity(serverUrl);
		socket.OnConnected += OnSocketConnected;
		socket.On("offer", OnOfferReceived);
		socket.Connect();
		
		StartCoroutine(WebRTC.Update());
	}

	// Update is called once per frame
	void Update()
	{
		
	}
	
	void OnDestory()
	{
		socket.Disconnect();
	}
	
	void OnApplicationClose()
	{
		socket.Disconnect();
	}
	
	private void OnSocketConnected (object sender, System.EventArgs e)
	{
		Debug.Log("Socket Connected");
		JoinRoom();
	}
	
	private void SetRemoteDescription(RTCSessionDescription sdp)
	{
		var op = peerConnection.SetRemoteDescription(ref sdp);
		while (!op.IsDone)
		{
			Debug.Log("Waiting for SetRemoteDescription to complete");
		}
		if (op.IsError)
		{
			Debug.LogError("SetRemoteDescription failed: " + op.Error.message);
			return;
		}
		else 
		{
			Debug.Log("SetRemoteDescription succeeded");
			isRemoteDescriptionSet = true;
		}
		return;
	}
	private void OnOfferReceived (SocketIOResponse e)
	{
		Debug.Log("Offer Received");
		peerConnection = new RTCPeerConnection();
		// TODO: use delegate instead of lambda
		// peerConnection.OnDataChannel += delegateOnDataChannel;
		stream = new MediaStream();
		
		stream.OnAddTrack = e => 
		{
			if (e.Track is VideoStreamTrack track)
			{
				Debug.Log("VideoStreamTrack");
				Debug.Log("Track kind: " + track.Kind);
				Debug.Log("Track id: " + track.Id);
				Debug.Log(track.ReadyState);
				Debug.Log(track.Enabled);
				Debug.LogWarning(track.Texture);
				// screen.GetComponent<Renderer>().material.mainTexture = track.Texture;
			}
		};
		peerConnection.OnDataChannel = e =>
		{
			Debug.Log("OnDataChannel");
			dataChannel = e;
			Debug.Log("Data channel state: " + dataChannel.ReadyState);
			Debug.Log("Data channel label: " + dataChannel.Label);
			dataChannel.OnMessage = bytes =>
			{
				Debug.Log("OnMessage");
				Debug.Log(Encoding.UTF8.GetString(bytes));
			};
		};	
		
		peerConnection.OnTrack = e =>
		{
			Debug.Log("OnTrack");
			if (e.Track is VideoStreamTrack track)
			{
				Debug.Log("VideoStreamTrack");
				stream.AddTrack(track);
				track.OnVideoReceived += tex =>
				{
					Debug.Log("OnVideoReceived");
					Debug.LogWarning(tex.GetType());
					Debug.LogWarning(tex.height);
					Debug.LogWarning(tex.width);
					Debug.LogWarning(tex.GetNativeTexturePtr());
					Debug.LogWarning(tex.GetNativeTexturePtr().ToInt32());
					screen.GetComponent<Renderer>().material.mainTexture = tex;
				};
			}
		};
		
		peerConnection.OnIceCandidate += iceCandidate =>
		{
			Debug.Log("OnIceCandidate");
			if (iceCandidate == null)
			{
				Debug.Log("IceCandidate is null");
				return;
			}
			var message = new 
			{
				room = roomName,
				name = "Unity",
				type = "candidate",
				candidate = iceCandidate.Candidate,
				sdpMid = iceCandidate.SdpMid,
				sdpMLineIndex = iceCandidate.SdpMLineIndex
			};
			socket.Emit("candidate", message);			
		};
		
		var sdp = ParseOfferMessage(e.ToString());
		SetRemoteDescription(sdp);
		
		if (isRemoteDescriptionSet)
		{
			CreateAnswerToOffer();
		}
		else 
		{
			return;
		}
	}
	
	private RTCSessionDescription ParseOfferMessage(string message)
	{
		Debug.Log("Parsing Offer Message");
		try
		{
			message = message.ToString().Substring(1, message.Length - 2);
			Debug.Log(message);
			var json = JObject.Parse(message);
			var offer = json["sdp"].ToString();
			var sdp = new RTCSessionDescription();
			sdp.type = RTCSdpType.Offer;
			sdp.sdp = offer;
			return sdp;
		}
		catch (System.Exception e)
		{
			Debug.LogError("Error parsing offer message: " + e.Message);
			throw;
		}
		
	}
	
	private void JoinRoom()
	{
		var message = new 
		{
			room = roomName,
			name = "Unity",
			type = "join"
		};
		
		socket.Emit("join", message);
	}
	
	
	private void OnDataChannelOpen()
	{
		Debug.Log("Data Channel Open");
	}
	private void OnDataChannelMessage(byte[] obj)
	{
		Debug.Log("Data Channel Message");
	}
	
	private void CreateAnswerToOffer()
	{
		Debug.Log("Creating Answer to Offer");
		var op = peerConnection.CreateAnswer();
		while (!op.IsDone)
		{
			Debug.Log("Waiting for CreateAnswer to complete");
		}
		if (op.IsError)
		{
			Debug.LogError("CreateAnswer failed: " + op.Error.message);
			return;
		}
		else 
		{
			Debug.Log("CreateAnswer succeeded");
		}
		
		SetLocalDescription(op.Desc);
		if (isLocalDescriptionSet)
		
		{
			SendAnswerToOffer();
		}
	}
	
	private void SetLocalDescription(RTCSessionDescription sdp)
	
	{
		Debug.Log("Setting Local Description");
		var op = peerConnection.SetLocalDescription(ref sdp);
		
		while (!op.IsDone)
		{
			Debug.Log("Waiting for SetLocalDescription to complete");
		}
		if (op.IsError)
		{
			Debug.LogError("SetLocalDescription failed: " + op.Error.message);
			return;
		}
		else 
		{
			Debug.Log("SetLocalDescription succeeded");
			isLocalDescriptionSet = true;
		}
	}
	
	private void SendAnswerToOffer()
	
	{
		Debug.Log("Sending Answer to Offer");
		var message = new 
		{
			room = roomName,
			name = "Unity",
			type = "answer",
			sdp = peerConnection.LocalDescription.sdp
		};
		
		socket.Emit("answer", message);
	}
}
