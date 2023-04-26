

<h1>mule-operator</h1>

<h3>An app for telepresence (remote operation of a physical, robotic representation of the user) by way of consumer Virtual Reality systems.</h3>

_________________________________

<h2>Environment</h2>

- Unity 2021.3.13f1 LTS (w/ Android Support module and OpenXR plugin installed)

- Android support module is installed with Unity via Unity Hub installer options

- OpenXR plugin package is installed via Unity's Package Manager within the project

- Build target: Android / OpenXR

_________________________________

<h2>App Setup / Installation</h2>

- At this time, these match the general steps for "sideloading" an app onto the Quest headset.

- Quest headset must have Developer Mode enabled (Requires a registered account/org with Oculus/Meta. See here: https://developer.oculus.com/documentation/native/android/mobile-device-setup/ )

- Connect Quest headset to PC via USB and ensure access has been granted to connect to the PC from within the headset itself

- Use ADB command-line or Meta Quest Developer Hub to push the apk from /LatestBuild/ to the headset (https://developer.oculus.com/meta-quest-developer-hub/)

- Unplug the USB cable and enter VR. The app will be listed after selecting "Unknown Sources" in the app-sorting drop down menu. If you do not see the "Unknown Sources" option, ensure that Developer Mode has been enabled. (see instructions linked above)
