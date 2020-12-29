import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:sdp_transform/sdp_transform.dart';
import 'package:flutter/services.dart';
import 'package:floating_action_bubble/floating_action_bubble.dart';

// import 'package:flutter_webrtc/web/rtc_session_description.dart';



void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Laser Cat',
      theme: ThemeData.dark(),
      home: MyHomePage(title: 'Laser Cat'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);
  final String title;
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with SingleTickerProviderStateMixin{
  TextStyle style = TextStyle(fontFamily: 'Montserrat', fontSize: 20.0);

  Animation<double> _animation;
  AnimationController _animationController;
  List<bool> isSelected = [false, true, false, false];

  bool _offer = false;
  RTCPeerConnection _peerConnection;
  MediaStream _localStream;
  RTCVideoRenderer _localRenderer = new RTCVideoRenderer();
  RTCVideoRenderer _remoteRenderer = new RTCVideoRenderer();


  final sdpController = TextEditingController();

  @override
  dispose() {
    _localRenderer.dispose();
    _remoteRenderer.dispose();
    sdpController.dispose();
    super.dispose();
  }

  @override
  void initState() {

    _animationController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 260),
    );

    final curvedAnimation = CurvedAnimation(curve: Curves.easeInOut, parent: _animationController);
    _animation = Tween<double>(begin: 0, end: 1).animate(curvedAnimation);

    initRenderers();
    _createPeerConnection().then((pc) {
      _peerConnection = pc;
    });
    super.initState();
  }

  initRenderers() async {
    await _localRenderer.initialize();
    await _remoteRenderer.initialize();
  }

  void _createOffer() async {
    RTCSessionDescription description =
    await _peerConnection.createOffer({'offerToReceiveVideo': 1});
    var session = parse(description.sdp);
    print(json.encode(session));
    _offer = true;

    // print(json.encode({
    //       'sdp': description.sdp.toString(),
    //       'type': description.type.toString(),
    //     }));

    _peerConnection.setLocalDescription(description);
  }

  void _createAnswer() async {
    RTCSessionDescription description =
    await _peerConnection.createAnswer({'offerToReceiveVideo': 1});

    var session = parse(description.sdp);
    print(json.encode(session));
    // print(json.encode({
    //       'sdp': description.sdp.toString(),
    //       'type': description.type.toString(),
    //     }));

    _peerConnection.setLocalDescription(description);
  }

  void _setRemoteDescription() async {
    String jsonString = sdpController.text;
    dynamic session = await jsonDecode('$jsonString');

    String sdp = write(session, null);

    // RTCSessionDescription description =
    //     new RTCSessionDescription(session['sdp'], session['type']);
    RTCSessionDescription description =
    new RTCSessionDescription(sdp, _offer ? 'answer' : 'offer');
    print(description.toMap());

    await _peerConnection.setRemoteDescription(description);
  }

  void _addCandidate() async {
    String jsonString = sdpController.text;
    dynamic session = await jsonDecode('$jsonString');
    print(session['candidate']);
    dynamic candidate =
    new RTCIceCandidate(session['candidate'], session['sdpMid'], session['sdpMlineIndex']);
    await _peerConnection.addCandidate(candidate);
  }

  _createPeerConnection() async {
    Map<String, dynamic> configuration = {
      "iceServers": [
        {"urls": "https://laserCat:a02c3192-3d45-11eb-8d2c-0242ac150003@global.xirsys.net/_turn/laserCat"},
      ]
    };

    final Map<String, dynamic> offerSdpConstraints = {
      "mandatory": {
        "OfferToReceiveAudio": true,
        "OfferToReceiveVideo": true,
      },
      "optional": [],
    };


    _localStream = await _getUserMedia();

    RTCPeerConnection pc = await createPeerConnection(configuration, offerSdpConstraints);
    // if (pc != null) print(pc);
    pc.addStream(_localStream);

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
      _remoteRenderer.srcObject = stream;
    };

    return pc;
  }

  _getUserMedia() async {
    final Map<String, dynamic> mediaConstraints = {
      'audio': false,
      'video': {
        'facingMode': 'user',
      },
    };

    MediaStream stream = await navigator.getUserMedia(mediaConstraints);

    // _localStream = stream;
    _localRenderer.srcObject = stream;
    // _localRenderer.mirror = true;

    // _peerConnection.addStream(stream);

    return stream;
  }

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
        // Flexible(
        //   child: new Container(
        //       key: new Key("remote"),
        //       margin: new EdgeInsets.fromLTRB(5.0, 5.0, 5.0, 5.0),
        //       decoration: new BoxDecoration(color: Colors.black),
        //       child: new RTCVideoView(_remoteRenderer)),
        // )
      ]));


  Row offerAndAnswerButtons() =>
      Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: <Widget>[
        new RaisedButton(
          // onPressed: () {
          //   return showDialog(
          //       context: context,
          //       builder: (context) {
          //         return AlertDialog(
          //           content: Text(sdpController.text),
          //         );
          //       });
          // },
          onPressed: _createOffer,
          child: Text('Offer'),
          color: Colors.amber,
        ),
        RaisedButton(
          onPressed: _createAnswer,
          child: Text('Answer'),
          color: Colors.amber,
        ),
      ]);

  Row sdpCandidateButtons() =>
      Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: <Widget>[
        RaisedButton(
          onPressed: _setRemoteDescription,
          child: Text('Set Remote Desc'),
          color: Colors.amber,
        ),
        RaisedButton(
          onPressed: _addCandidate,
          child: Text('Add Candidate'),
          color: Colors.amber,
        )
      ]);

  Padding sdpCandidatesTF() => Padding(
    padding: const EdgeInsets.all(16.0),
    child: TextField(
      controller: sdpController,
      keyboardType: TextInputType.multiline,
      maxLines: 4,
      maxLength: TextField.noMaxLength,
    ),
  );

  void cameraHandler(bool isOn){
    if (isOn){
      _createOffer();
      //turnOff
    }else{
      //turnOn
    }
  }

  @override
  Widget build(BuildContext context) {
    // List<bool> isSelected = [false, true, false, false];

    // SystemChrome.setPreferredOrientations([
    //   DeviceOrientation.landscapeLeft,
    //   DeviceOrientation.landscapeRight,
    // ]);

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
                    isSelected[index] = !isSelected[index];
                  });
                  if (index == 0) /*settingsHandler(isSelected[index])*/;
                  else if (index == 1) cameraHandler(isSelected[index]);
                  else if (index == 2) /*gameHandler(isSelected[index])*/;
                  else /*foodHandler*/;
                },
                isSelected: isSelected,
              ),
            ],
          ),
        ),


        // floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
        //
        //Init Floating Action Bubble
        // floatingActionButton: FloatingActionBubble(
        //   backGroundColor: Colors.white,
        //   // Menu items
        //   items: <Bubble>[
        //
        //     // Floating action menu item
        //     Bubble(
        //       title:"Circle",
        //       iconColor :Colors.white,
        //       bubbleColor : Colors.blue,
        //       icon:Icons.circle,
        //       titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
        //       onPress: () {
        //         _animationController.reverse();
        //       },
        //     ),
        //     // Floating action menu item
        //     Bubble(
        //       title:"Random",
        //       iconColor :Colors.white,
        //       bubbleColor : Colors.blue,
        //       icon:Icons.play_for_work_outlined,
        //       titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
        //       onPress: () {
        //         _animationController.reverse();
        //       },
        //     ),
        //     // Floating action menu item
        //     Bubble(
        //       title:"Square",
        //       iconColor :Colors.white,
        //       bubbleColor : Colors.blue,
        //       icon:Icons.square_foot,
        //       titleStyle:TextStyle(fontSize: 16 , color: Colors.white),
        //       onPress: () {
        //         _animationController.reverse();
        //       },
        //     )
        //   ],
        //
        //   // animation controller
        //   animation: _animation,
        //
        //   // On pressed change animation state
        //   onPress: _animationController.isCompleted
        //       ? _animationController.reverse
        //       : _animationController.forward,
        //
        //   // Floating Action button Icon color
        //   iconColor: Colors.blue,

          // Flaoting Action button Icon
          // icon: AnimatedIcons.list_view,
        // )
    );
  }
  //   return Scaffold(
  //       appBar: AppBar(
  //         title: Text(widget.title),
  //       ),
  //       body: Container(
  //           child: Column(children: [
  //             videoRenderers(),
  //             offerAndAnswerButtons(),
  //             // sdpCandidatesTF(),
  //             // sdpCandidateButtons(),
  //           ])));
  // }
}



// import 'package:flutter/material.dart';
// import 'package:flutter_webrtc/flutter_webrtc.dart';
//
// void main() {
//   runApp(MyApp());
// }
//
// class MyApp extends StatelessWidget {
//   // This widget is the root of your application.
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       debugShowCheckedModeBanner: false,
//       title: 'Laser Cat',
//       theme: ThemeData(
//         primarySwatch: Colors.blue,
//       ),
//       home: MyHomePage(title: 'Laser Cat'),
//     );
//   }
// }
//
// class MyHomePage extends StatefulWidget {
//   MyHomePage({Key key, this.title}) : super(key: key);
//   final String title;
//
//   @override
//   _MyHomePageState createState() => _MyHomePageState();
// }
//
// class _MyHomePageState extends State<MyHomePage> {
//
//   final _localRenderer = new RTCVideoRenderer();
//
//   @override
//   dispose(){
//     _localRenderer.dispose();
//     super.dispose();
//   }
//
//   @override
//   void initState() {
//     initRenderers();
//     _getUserMedia();
//     super.initState();
//   }
//
//   initRenderers() async{
//       await _localRenderer.initialize();
//   }
//
//   _getUserMedia() async {
//     final Map<String, dynamic> mediaConstraints = {
//       'audio': false,
//       'video': {
//         'facingMode': 'user',
//       },
//     };
//
//     MediaStream stream = await navigator.getUserMedia(mediaConstraints);
//
//     _localRenderer.srcObject = stream;
//
//   }
//
//   @override
//   Widget build(BuildContext context) {
//
//     return Scaffold(
//       appBar: AppBar(
//         title: Text(widget.title),
//       ),
//       body: Container(
//           child: new Stack(
//               children: <Widget>[
//                 Positioned(
//                   top: 0.0,
//                   right: 0.0,
//                   left: 0.0,
//                   bottom: 0.0,
//                   child: new Container(
//                     child: new RTCVideoView(_localRenderer),
//                   ),
//                 )
//               ],
//           ),
//       ),
//     );
//   }
// }
