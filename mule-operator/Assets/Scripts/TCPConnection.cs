using System;
using System.IO;
using System.Net.Sockets;
using UnityEngine;

public class TCPConnection 
{

    private TcpClient client;
    private NetworkStream networkStream;
    private StreamReader streamReader;
    private StreamWriter streamWriter;

    public TCPConnection() { }
    public void ConnectToServer(string serverIP, int serverPort)
    {
        try
        {
            client = new TcpClient(serverIP, serverPort);
            networkStream = client.GetStream();
            streamReader = new StreamReader(networkStream);
            streamWriter = new StreamWriter(networkStream);

            Debug.Log("Connected to server: " + serverIP + ":" + serverPort);
        }
        catch (Exception e)
        {
            Debug.LogError("Error connecting to server: " + e.Message);
        }
    }

    public bool IsConnectionValid()
    {
        return client.Connected;
    }
    public string SendJsonMessage(object messageObject)
    {
        if (client == null || !client.Connected)
        {
            Debug.LogError("Not connected to server.");
            return null;
        }

        try
        {
            string jsonMessage = JsonUtility.ToJson(messageObject);
            streamWriter.WriteLine(jsonMessage);
            streamWriter.Flush();

            string response = streamReader.ReadLine();
            return response;
        }
        catch (Exception e)
        {
            Debug.LogError("Error sending JSON message: " + e.Message);
            return null;
        }
    }
    
    public void DisconnectFromServer()
    {
        if (client != null)
        {
            client.Close();
            client = null;
        }

        if (networkStream != null)
        {
            networkStream.Close();
            networkStream = null;
        }

        if (streamReader != null)
        {
            streamReader.Close();
            streamReader = null;
        }

        if (streamWriter != null)
        {
            streamWriter.Close();
            streamWriter = null;
        }
    }
}
