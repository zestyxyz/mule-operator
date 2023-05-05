using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ServerConnection : MonoBehaviour
{
    private Vector3 cameraRotation;
    private TCPConnection connection;

    public string serverIP = "127.0.0.1";
    public int serverPort = 8080;
    // Start is called before the first frame update
    void Start()
    {
        connection = new TCPConnection();
        connection.ConnectToServer(serverIP, serverPort);
    }

    // Update is called once per frame
    void Update()
    {
        // get the rotation of the camera
        cameraRotation = transform.rotation.eulerAngles;

        // check if connection is valid
        if (connection.IsConnectionValid())
        {
            var message = new RotationMessage();
            message.type = "camera_rotation";
            message.x = cameraRotation.x;
            message.y = cameraRotation.y;
            message.z = cameraRotation.z;
            connection.SendJsonMessage(message);
        }

    }

    private void OnApplicationQuit()
    {
        connection.DisconnectFromServer();
    }
}
