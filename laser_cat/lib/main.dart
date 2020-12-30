import 'package:flutter/material.dart';
import 'package:floating_action_bubble/floating_action_bubble.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:sdp_transform/sdp_transform.dart';

// Import the firebase_core plugin
import 'package:firebase_core/firebase_core.dart';



void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // Create the initialization Future outside of `build`:
  final Future<FirebaseApp> _initialization = Firebase.initializeApp();


  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Laser Cat',
      theme: ThemeData.dark(),
      home: CameraPage(),
    );
  }
}

// class MyHomePage extends StatefulWidget {
//   MyHomePage({Key key, this.title}) : super(key: key);
//   final String title;
//
//   @override
//   _MyHomePageState createState() => _MyHomePageState();
// }



// class _MyHomePageState extends State<MyHomePage> {
//   TextStyle style = TextStyle(fontFamily: 'Montserrat', fontSize: 20.0);
//
//   void _login() {
//     Navigator.push(
//       context,
//       MaterialPageRoute(builder: (context) => CameraPage()),
//     );
//   }
//
//
//   @override
//   Widget build(BuildContext context) {
//
//     final emailField = TextField(
//       obscureText: false,
//       style: style,
//       decoration: InputDecoration(
//           contentPadding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
//           hintText: "Email",
//           border:
//           OutlineInputBorder(borderRadius: BorderRadius.circular(32.0))),
//     );
//     final passwordField = TextField(
//       obscureText: true,
//       style: style,
//       decoration: InputDecoration(
//           contentPadding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
//           hintText: "Password",
//           border:
//           OutlineInputBorder(borderRadius: BorderRadius.circular(32.0))),
//     );
//     final loginButon = Material(
//       elevation: 5.0,
//       borderRadius: BorderRadius.circular(30.0),
//       color: Color(0xff01A0C7),
//       child: MaterialButton(
//         minWidth: MediaQuery.of(context).size.width,
//         padding: EdgeInsets.fromLTRB(20.0, 15.0, 20.0, 15.0),
//         onPressed: _login,
//         child: Text("Login",
//             textAlign: TextAlign.center,
//             style: style.copyWith(
//                 color: Colors.white, fontWeight: FontWeight.bold)),
//       ),
//     );
//
//     return Scaffold(
//       body: Center(
//         child: Container(
//           // color: Colors.blueAccent,
//           child: Padding(
//             padding: const EdgeInsets.all(36.0),
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.center,
//               mainAxisAlignment: MainAxisAlignment.center,
//               children: <Widget>[
//                 SizedBox(
//                   height: 130.0,
//                   child: Image.asset(
//                     'assets/images/laserCat.png',
//                     fit: BoxFit.contain,
//                   ),
//                 ),
//                 SizedBox(height: 10.0),
//                 emailField,
//                 SizedBox(height: 5.0),
//                 passwordField,
//                 SizedBox(
//                   height: 5.0,
//                 ),
//                 loginButon,
//                 SizedBox(
//                   height: 5.0,
//                 )
//               ],
//             ),
//           ),
//         ),
//       ),
//     );
//   }
// }


class CameraPage extends StatefulWidget {
  CameraPage({Key key}) : super(key: key);

  @override
  State<StatefulWidget> createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> with SingleTickerProviderStateMixin{
  // initialized for widget
  Animation<double> _animation;
  AnimationController _animationController;
  List<bool> isSelected = [false, true, false, false];


  //initialized for web-rct (for the video stream)
  bool _offer = false;
  RTCVideoRenderer _localRenderer = new RTCVideoRenderer();
  RTCPeerConnection _peerConnection;
  MediaStream _localStream;

  @override
  void initState(){

    // initialized for widget
    _animationController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 260),
    );

    // initialized for widget
    final curvedAnimation = CurvedAnimation(curve: Curves.easeInOut, parent: _animationController);
    _animation = Tween<double>(begin: 0, end: 1).animate(curvedAnimation);

    // initialized for web-rct (for the video stream)
    initRenderers();

    //@Todo
    //get from the firestore the configutation for connection
    //set a connection
    //set the stream
    /// the next function is from other project. We can use some of it.
    // _createPeerConnection().then((pc) {
    //   _peerConnection = pc;
    // });

    super.initState();
  }

  //some function that has to be with renderer
  @override
  dispose() {
    _localRenderer.dispose();
    super.dispose();
  }


  _createPeerConnection() async {
    //stun server configuration
    Map<String, dynamic> configuration = {
      'iceServers': [{
        'urls': [ "stun:eu-turn1.xirsys.com"
      ]}, {
        'username': "AXvda82o0ZFaQwGtNY9UkcAlVCgMsi0Y6wJ9Igv2elkXse7wRFrAPFWWBtqS-pAoAAAAAF_sXvlsYXNlckNhdA==",
        'credential': "edbd6ccc-4a8e-11eb-a84a-0242ac140004",
        'urls': [
          "turn:eu-turn1.xirsys.com:80?transport=udp",
          "turn:eu-turn1.xirsys.com:3478?transport=udp",
          "turn:eu-turn1.xirsys.com:80?transport=tcp",
          "turn:eu-turn1.xirsys.com:3478?transport=tcp",
          "turns:eu-turn1.xirsys.com:443?transport=tcp",
          "turns:eu-turn1.xirsys.com:5349?transport=tcp"
        ]
      }]
    };

    //constains to sent to the offer
    final Map<String, dynamic> offerSdpConstraints = {
      "mandatory": {
        "OfferToReceiveAudio": true,
        "OfferToReceiveVideo": true,
      },
      "optional": [],
    };

    //the wait makes problems. need to understand what to do
    RTCPeerConnection pc = await createPeerConnection(configuration, offerSdpConstraints);
    if (pc != null) print(pc);

    pc.onIceCandidate = (e) {
      if (e.candidate != null) {
        print(json.encode({
          'candidate': e.candidate.toString(),
          'sdpMid': e.sdpMid.toString(),
          'sdpMlineIndex': e.sdpMlineIndex,
        }));
      }
    };

    pc.onIceConnectionState = (e) {
      print(e);
    };

    pc.onAddStream = (stream) {
      print('addStream: ' + stream.id);
      _localRenderer.srcObject = stream;
    };

    return pc;
  }

  //some helper function to the video controll
  initRenderers() async {
    await _localRenderer.initialize();
  }

  //make the video to show in the app
  Container videoRenderers() => Container(
      child: Row(children: [
        Flexible(
          child: new Container(
          key: new Key("local"),
          margin: new EdgeInsets.fromLTRB(10.0, 10.0, 10.0, 10.0),
          // decoration: new BoxDecoration(color: Colors.black),
            child: new RTCVideoView(_localRenderer)
          ),
        ),
      ])
  );

  //helper function to establish the connection
  void _createOffer() async {
    RTCSessionDescription description =
    await _peerConnection.createOffer({'offerToReceiveVideo': 1});
    // var session = parse(description.sdp);
    // print(json.encode(session));
    _offer = true;
    _peerConnection.setLocalDescription(description);
  }

  void cameraHandler(bool isOn){
    if (isOn){
      //turnOff
    }else{
      // _createOffer();
    }
  }

  void settingsHandler(bool isOn){
    if (isOn){
      //turnOff
    }else{
      // _createOffer();
    }
  }

  void gameHandler(bool isOn){
    if (isOn){
      //turnOff
    }else{
      // _createOffer();
    }
  }

  void foodHandler(bool isOn){
    if (isOn){
      //turnOff
    }else{
      // _createOffer();
    }
  }

  //main bulder - the app screen (UI)
  @override
  Widget build(BuildContext context) {
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
    return Scaffold(
        appBar: AppBar(
          title: Text("Laser Cat"),
        ),
        body: Center(
          child: Column(
            children: <Widget>[
              Expanded(
                child: Container(
                  child: videoRenderers(),
                ),
              ),
              ToggleButtons(
                children: <Widget>[
                  Icon(Icons.settings),
                  Icon(Icons.camera),
                  Icon(Icons.play_arrow),
                  Icon(Icons.fastfood),
                ],
                onPressed: (int index) {
                  setState(() {
                  });
                  isSelected[index] = !isSelected[index];
                  if (index == 0) isSelected[index] = !isSelected[index] /*settingsHandler(isSelected[index])*/;
                  else if (index == 1) cameraHandler(isSelected[index]);
                  else if (index == 2) /*gameHandler(isSelected[index])*/;
                  else isSelected[index] = !isSelected[index] /*foodHandler*/;
                },
                isSelected: isSelected,
              ),
            ],
          ),
        ),


        floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,

        //Init Floating Action Bubble
        floatingActionButton: FloatingActionBubble(
          backGroundColor: Colors.blue,
          // Menu items
          items: <Bubble>[

            // Floating action menu item
            Bubble(
              title:"Circle",
              iconColor :Colors.white,
              bubbleColor : Colors.blue,
              icon:Icons.circle,
              titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
              onPress: () {
                _animationController.reverse();
              },
            ),
            // Floating action menu item
            Bubble(
              title:"Random",
              iconColor :Colors.white,
              bubbleColor : Colors.blue,
              icon:Icons.play_for_work_outlined,
              titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
              onPress: () {
                _animationController.reverse();
              },
            ),
            // Floating action menu item
            Bubble(
              title:"Square",
              iconColor :Colors.white,
              bubbleColor : Colors.blue,
              icon:Icons.square_foot,
              titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
              onPress: () {
                _animationController.reverse();
                /*send_square_signal();*/
              },
            )
          ],

          // animation controller
          animation: _animation,

          // On pressed change animation state
          onPress: _animationController.isCompleted
              ? _animationController.reverse
              : _animationController.forward,

          // Floating Action button Icon color
          iconColor: Colors.blue,

          // Flaoting Action button Icon
          animatedIconData: AnimatedIcons.list_view,
        )
    );
  }
}