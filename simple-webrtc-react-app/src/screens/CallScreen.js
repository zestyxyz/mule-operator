import { useParams } from "react-router-dom";
import { useRef, useEffect } from "react";
import socketio from "socket.io-client";
import "./CallScreen.css";
import { CreateJoinMessage } from "./Message";
import { type } from "@testing-library/user-event/dist/type";

function CallScreen() {
  const params = useParams();
  const localUsername = params.username;
  const roomName = params.room;
  const remoteVideoRef = useRef(null);

  const socket = socketio("http://192.168.2.11:9000", {
    autoConnect: false,
  });

  let pc; // For RTCPeerConnection Object

  const sendData = (data) => {
    socket.emit("data", {
      username: localUsername,
      room: roomName,
      data: data,
    });
  };

  const startConnection = () => {
    try 
    {
      socket.connect();
      socket.emit("join", CreateJoinMessage(localUsername, "join", roomName));
    }
    catch (error){
      console.error("Stream not found: ", error);
    };
  };

  const onIceCandidate = (event) => {
    if (event.candidate) {
      console.log("Sending ICE candidate");
      // sendData({
      //   type: "candidate",
      //   candidate: event.candidate,
      // });
      var message = {
        type: "candidate",
        candidate: event.candidate,
        origin : localUsername,
        room : roomName
      }
      socket.emit("candidate", message)
    }
  };

  const onTrack = (event) => {
    console.log("Adding remote track");
    remoteVideoRef.current.srcObject = event.streams[0];
  };

  const createPeerConnection = () => {
    try {
      // pc = new RTCPeerConnection({
      //   iceServers: [
      //     {
      //       urls: "stun:openrelay.metered.ca:80",
      //     },
      //     {
      //       urls: "turn:openrelay.metered.ca:80",
      //       username: "openrelayproject",
      //       credential: "openrelayproject",
      //     },
      //     {
      //       urls: "turn:openrelay.metered.ca:443",
      //       username: "openrelayproject",
      //       credential: "openrelayproject",
      //     },
      //     {
      //       urls: "turn:openrelay.metered.ca:443?transport=tcp",
      //       username: "openrelayproject",
      //       credential: "openrelayproject",
      //     },
      //   ],
      // });
      pc = new RTCPeerConnection();
      pc.onicecandidate = onIceCandidate;
      pc.ontrack = onTrack;
      pc.ondatachannel = (event) => {
        console.log("Datachannel event " + event);
        const receiveChannel = event.channel;
        receiveChannel.onmessage = (event) => {
          console.log("Message received: " + event.data);
        };
        receiveChannel.onopen = () => {
          console.log("Data channel is open and ready to be used.");
        };
        receiveChannel.onclose = () => {
          console.log("Data channel is closed.");
        };
      };
      console.log("PeerConnection created");
    } catch (error) {
      console.error("PeerConnection failed: ", error);
    }
  };

  const setAndSendLocalDescription = (sessionDescription) => {
    pc.setLocalDescription(sessionDescription);
    console.log("Local description set");

    var message = {
      type: sessionDescription.type,
      sdp: sessionDescription.sdp,
      origin : localUsername,
      room : roomName,
    }
    socket.emit("answer", message)
  };

  const sendOffer = () => {
    console.log("Sending offer");
    pc.createOffer().then(setAndSendLocalDescription, (error) => {
      console.error("Send offer failed: ", error);
    });
  };

  const sendAnswer = () => {
    console.log("Sending answer");
    pc.createAnswer().then(setAndSendLocalDescription, (error) => {
      console.error("Send answer failed: ", error);
    });
  };

  const signalingDataHandler = (data) => {
    if (data.type === "offer") {
      console.log("Received offer");
      console.log(data);
     
    } else if (data.type === "answer") {
      pc.setRemoteDescription(new RTCSessionDescription(data));
    } else if (data.type === "candidate") {
      pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    } else {
      console.log("Unknown Data");
    }
  };

  socket.on("ready", () => {
    console.log("Ready to Connect!");
    createPeerConnection();
    sendOffer();
  });

  socket.on("client_connected", () => {
    console.log("client_connected  asdasdsdaasd!");
  });

  socket.on("offer", (data) => {
    data = JSON.parse(data);
    console.log("Data received: ", data);
    console.log(data.sdp)
    createPeerConnection();
    var desc = new RTCSessionDescription
    ({
      type: "offer",
      sdp: data.sdp,
    });
    
    pc.setRemoteDescription(desc);
    sendAnswer();
  });

  useEffect(() => {
    startConnection();
    return function cleanup() {
      pc?.close();
    };
  }, []);

  return (
    <div>
      <label>{"Username: " + localUsername}</label>
      <label>{"Room Id: " + roomName}</label>
      <video autoPlay muted playsInline ref={remoteVideoRef} />
    </div>
  );
}

export default CallScreen;
