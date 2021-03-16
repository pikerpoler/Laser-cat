import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
from signaling import wait_for_message, send_message

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

ROOT = os.path.dirname(__file__)


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request,candidate):
    request = json.loads(request) # await request.json()
    candidate = json.loads(candidate)
    print(request)
    print(candidate)
#     print("params:\n",params)
    offer = RTCSessionDescription(sdp=request, type="offer")

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)
    
    # open media source
    if False: # args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        if platform.system() == "Darwin":
            player = MediaPlayer("default:none", format="avfoundation", options=options)
        else:
            player = MediaPlayer("/dev/video0", format="v4l2", options=options)
    print(pc.remoteDescription)
    await pc.setRemoteDescription(offer)
    print(pc.remoteDescription)
    for t in pc.getTransceivers():
        if t.kind == "audio" and player.audio:
            pc.addTrack(player.audio)
        elif t.kind == "video" and player.video:
            pc.addTrack(player.video)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await pc.addIceCandidate(candidate_from_sdp(candidate))
    print(pc.localDescription)
    
    return json.dumps(pc.localDescription.sdp)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()

def candidate_from_sdp(sdp: str) -> RTCIceCandidate:
    bits = sdp.split()
    assert len(bits) >= 8

    candidate = RTCIceCandidate(
        component=int(bits[1]),
        foundation=bits[0],
        ip=bits[4],
        port=int(bits[5]),
        priority=int(bits[3]),
        protocol=bits[2],
        type=bits[7],
    )

    for i in range(8, len(bits) - 1, 2):
        if bits[i] == "raddr":
            candidate.relatedAddress = bits[i + 1]
        elif bits[i] == "rport":
            candidate.relatedPort = int(bits[i + 1])
        elif bits[i] == "tcptype":
            candidate.tcpType = bits[i + 1]

    return candidate

def object_from_string(message_str):
    message = json.loads(message_str)
    if message["type"] in ["answer", "offer"]:
        return RTCSessionDescription(**message)
    elif message["type"] == "candidate" and message["candidate"]:
        candidate = candidate_from_sdp(message["candidate"].split(":", 1)[1])
        candidate.sdpMid = message["id"]
        candidate.sdpMLineIndex = message["label"]
        return candidate
    elif message["type"] == "bye":
        return BYE


def object_to_string(obj):
    if isinstance(obj, RTCSessionDescription):
        message = {"sdp": obj.sdp, "type": obj.type}
    elif isinstance(obj, RTCIceCandidate):
        message = {
            "candidate": "candidate:" + candidate_to_sdp(obj),
            "id": obj.sdpMid,
            "label": obj.sdpMLineIndex,
            "type": "candidate",
        }
    else:
        assert obj is BYE
        message = {"type": "bye"}
    return json.dumps(message, sort_keys=True)



async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()



async def run():
    
    
    pc = RTCPeerConnection()
    if False: # args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        if platform.system() == "Darwin":
            player = MediaPlayer("default:none", format="avfoundation", options=options)
        else:
            player = MediaPlayer("/dev/video0", format="v4l2", options=options)
            
    def add_tracks():
#         if player and player.audio:
#             pc.addTrack(player.audio)
        pc.addTrack(player.video)


    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)


    # connect signaling

    if role == "offer":
        # send offer
        add_tracks()
        await pc.setLocalDescription(await pc.createOffer())
        send_message("OFFER",pc.localDescription)

    # consume signaling
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)

            if obj.type == "offer":
                # send answer
                add_tracks()
                await pc.setLocalDescription(await pc.createAnswer())
                await send_message("ANSWER",pc.localDescription))
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break



if __name__ == "__main__":
    rrr = 'v=0\r\no=- 3490562090973527459 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0 1\r\na=msid-semantic: WMS\r\nm=video 50653 UDP/TLS/RTP/SAVPF 96 97 98 99 125 100 101 102 124 104 123 106 107 108 109 127\r\nc=IN IP4 109.65.191.252\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=candidate:2283241699 1 udp 2113937151 f96ed977-339b-4e44-94eb-53c5b4b0601b.local 50653 typ host generation 0 network-cost 999\r\na=candidate:842163049 1 udp 1677729535 109.65.191.252 50653 typ srflx raddr 0.0.0.0 rport 0 generation 0 network-cost 999\r\na=ice-ufrag:UbzI\r\na=ice-pwd:nr2/yOtf0DOZ3e2UDtxJTE53\r\na=ice-options:trickle\r\na=fingerprint:sha-256 8E:B0:2E:C8:57:66:AB:13:C5:69:3C:D7:71:05:FD:0C:60:02:37:72:B8:A3:4E:85:40:CE:49:47:FF:5A:44:E1\r\na=setup:actpass\r\na=mid:0\r\na=extmap:1 urn:ietf:params:rtp-hdrext:toffset\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:3 urn:3gpp:video-orientation\r\na=extmap:4 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=extmap:5 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay\r\na=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type\r\na=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-timing\r\na=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/color-space\r\na=extmap:9 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=extmap:10 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id\r\na=extmap:11 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id\r\na=recvonly\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=rtpmap:96 VP8/90000\r\na=rtcp-fb:96 goog-remb\r\na=rtcp-fb:96 transport-cc\r\na=rtcp-fb:96 ccm fir\r\na=rtcp-fb:96 nack\r\na=rtcp-fb:96 nack pli\r\na=rtpmap:97 rtx/90000\r\na=fmtp:97 apt=96\r\na=rtpmap:98 VP9/90000\r\na=rtcp-fb:98 goog-remb\r\na=rtcp-fb:98 transport-cc\r\na=rtcp-fb:98 ccm fir\r\na=rtcp-fb:98 nack\r\na=rtcp-fb:98 nack pli\r\na=fmtp:98 profile-id=0\r\na=rtpmap:99 rtx/90000\r\na=fmtp:99 apt=98\r\na=rtpmap:125 VP9/90000\r\na=rtcp-fb:125 goog-remb\r\na=rtcp-fb:125 transport-cc\r\na=rtcp-fb:125 ccm fir\r\na=rtcp-fb:125 nack\r\na=rtcp-fb:125 nack pli\r\na=fmtp:125 profile-id=1\r\na=rtpmap:100 H264/90000\r\na=rtcp-fb:100 goog-remb\r\na=rtcp-fb:100 transport-cc\r\na=rtcp-fb:100 ccm fir\r\na=rtcp-fb:100 nack\r\na=rtcp-fb:100 nack pli\r\na=fmtp:100 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f\r\na=rtpmap:101 rtx/90000\r\na=fmtp:101 apt=100\r\na=rtpmap:102 H264/90000\r\na=rtcp-fb:102 goog-remb\r\na=rtcp-fb:102 transport-cc\r\na=rtcp-fb:102 ccm fir\r\na=rtcp-fb:102 nack\r\na=rtcp-fb:102 nack pli\r\na=fmtp:102 level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42001f\r\na=rtpmap:124 rtx/90000\r\na=fmtp:124 apt=102\r\na=rtpmap:104 H264/90000\r\na=rtcp-fb:104 goog-remb\r\na=rtcp-fb:104 transport-cc\r\na=rtcp-fb:104 ccm fir\r\na=rtcp-fb:104 nack\r\na=rtcp-fb:104 nack pli\r\na=fmtp:104 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f\r\na=rtpmap:123 rtx/90000\r\na=fmtp:123 apt=104\r\na=rtpmap:106 H264/90000\r\na=rtcp-fb:106 goog-remb\r\na=rtcp-fb:106 transport-cc\r\na=rtcp-fb:106 ccm fir\r\na=rtcp-fb:106 nack\r\na=rtcp-fb:106 nack pli\r\na=fmtp:106 level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42e01f\r\na=rtpmap:107 rtx/90000\r\na=fmtp:107 apt=106\r\na=rtpmap:108 red/90000\r\na=rtpmap:109 rtx/90000\r\na=fmtp:109 apt=108\r\na=rtpmap:127 ulpfec/90000\r\nm=audio 38042 UDP/TLS/RTP/SAVPF 111 103 9 0 8 105 13 110 113 126\r\nc=IN IP4 109.65.191.252\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=candidate:2283241699 1 udp 2113937151 f96ed977-339b-4e44-94eb-53c5b4b0601b.local 38042 typ host generation 0 network-cost 999\r\na=candidate:842163049 1 udp 1677729535 109.65.191.252 38042 typ srflx raddr 0.0.0.0 rport 0 generation 0 network-cost 999\r\na=ice-ufrag:UbzI\r\na=ice-pwd:nr2/yOtf0DOZ3e2UDtxJTE53\r\na=ice-options:trickle\r\na=fingerprint:sha-256 8E:B0:2E:C8:57:66:AB:13:C5:69:3C:D7:71:05:FD:0C:60:02:37:72:B8:A3:4E:85:40:CE:49:47:FF:5A:44:E1\r\na=setup:actpass\r\na=mid:1\r\na=extmap:14 urn:ietf:params:rtp-hdrext:ssrc-audio-level\r\na=extmap:2 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time\r\na=extmap:4 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01\r\na=extmap:9 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=extmap:10 urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id\r\na=extmap:11 urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id\r\na=recvonly\r\na=rtcp-mux\r\na=rtpmap:111 opus/48000/2\r\na=rtcp-fb:111 transport-cc\r\na=fmtp:111 minptime=10;useinbandfec=1\r\na=rtpmap:103 ISAC/16000\r\na=rtpmap:9 G722/8000\r\na=rtpmap:0 PCMU/8000\r\na=rtpmap:8 PCMA/8000\r\na=rtpmap:105 CN/16000\r\na=rtpmap:13 CN/8000\r\na=rtpmap:110 telephone-event/48000\r\na=rtpmap:113 telephone-event/16000\r\na=rtpmap:126 telephone-event/8000\r\n'
    
    request = '{"version":0,"origin":{"username":"-","sessionId":246986351456661200,"sessionVersion":2,"netType":"IN","ipVer":4,"address":"127.0.0.1"},"name":"-","invalid":[{"value":"-"}],"timing":{"start":0,"stop":0},"groups":[{"type":"BUNDLE","mids":0}],"msidSemantic":{"semantic":"WMS","token":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl"},"media":[{"rtp":[{"payload":96,"codec":"VP8","rate":90000,"encoding":null},{"payload":97,"codec":"rtx","rate":90000,"encoding":null},{"payload":98,"codec":"VP9","rate":90000,"encoding":null},{"payload":99,"codec":"rtx","rate":90000,"encoding":null},{"payload":100,"codec":"VP9","rate":90000,"encoding":null},{"payload":101,"codec":"rtx","rate":90000,"encoding":null},{"payload":102,"codec":"H264","rate":90000,"encoding":null},{"payload":121,"codec":"rtx","rate":90000,"encoding":null},{"payload":127,"codec":"H264","rate":90000,"encoding":null},{"payload":120,"codec":"rtx","rate":90000,"encoding":null},{"payload":125,"codec":"H264","rate":90000,"encoding":null},{"payload":107,"codec":"rtx","rate":90000,"encoding":null},{"payload":108,"codec":"H264","rate":90000,"encoding":null},{"payload":109,"codec":"rtx","rate":90000,"encoding":null},{"payload":124,"codec":"H264","rate":90000,"encoding":null},{"payload":119,"codec":"rtx","rate":90000,"encoding":null},{"payload":123,"codec":"H264","rate":90000,"encoding":null},{"payload":118,"codec":"rtx","rate":90000,"encoding":null},{"payload":114,"codec":"red","rate":90000,"encoding":null},{"payload":115,"codec":"rtx","rate":90000,"encoding":null},{"payload":116,"codec":"ulpfec","rate":90000,"encoding":null}],"fmtp":[{"payload":97,"config":"apt=96"},{"payload":98,"config":"profile-id=0"},{"payload":99,"config":"apt=98"},{"payload":100,"config":"profile-id=2"},{"payload":101,"config":"apt=100"},{"payload":102,"config":"level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f"},{"payload":121,"config":"apt=102"},{"payload":127,"config":"level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42001f"},{"payload":120,"config":"apt=127"},{"payload":125,"config":"level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f"},{"payload":107,"config":"apt=125"},{"payload":108,"config":"level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42e01f"},{"payload":109,"config":"apt=108"},{"payload":124,"config":"level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=4d001f"},{"payload":119,"config":"apt=124"},{"payload":123,"config":"level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=64001f"},{"payload":118,"config":"apt=123"},{"payload":115,"config":"apt=114"}],"type":"video","port":9,"protocol":"UDP/TLS/RTP/SAVPF","payloads":"96 97 98 99 100 101 102 121 127 120 125 107 108 109 124 119 123 118 114 115 116","connection":{"version":4,"ip":"0.0.0.0"},"rtcp":{"port":9,"netType":"IN","ipVer":4,"address":"0.0.0.0"},"iceUfrag":"pj4Y","icePwd":"Qx6BPdQ4bCCb0E/jab0spQi2","iceOptions":"trickle","fingerprint":{"type":"sha-256","hash":"A8:EF:FF:9F:38:09:D5:9D:79:CB:4A:FE:33:8F:DA:07:27:0B:D4:64:A0:1A:DD:D6:2A:07:12:EE:E1:7F:10:9E"},"setup":"actpass","mid":0,"ext":[{"value":1,"direction":null,"uri":"urn:ietf:params:rtp-hdrext:toffset","config":null},{"value":2,"direction":null,"uri":"http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time","config":null},{"value":3,"direction":null,"uri":"urn:3gpp:video-orientation","config":null},{"value":4,"direction":null,"uri":"http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01","config":null},{"value":5,"direction":null,"uri":"http://www.webrtc.org/experiments/rtp-hdrext/playout-delay","config":null},{"value":6,"direction":null,"uri":"http://www.webrtc.org/experiments/rtp-hdrext/video-content-type","config":null},{"value":7,"direction":null,"uri":"http://www.webrtc.org/experiments/rtp-hdrext/video-timing","config":null},{"value":8,"direction":null,"uri":"http://www.webrtc.org/experiments/rtp-hdrext/color-space","config":null},{"value":9,"direction":null,"uri":"urn:ietf:params:rtp-hdrext:sdes:mid","config":null},{"value":10,"direction":null,"uri":"urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id","config":null},{"value":11,"direction":null,"uri":"urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id","config":null}],"direction":"sendrecv","msid":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl 19aa5442-043c-403e-a9de-e73eea59ebe1","rtcpMux":"rtcp-mux","rtcpRsize":"rtcp-rsize","rtcpFb":[{"payload":96,"type":"goog-remb","subtype":null},{"payload":96,"type":"transport-cc","subtype":null},{"payload":96,"type":"ccm","subtype":"fir"},{"payload":96,"type":"nack","subtype":null},{"payload":96,"type":"nack","subtype":"pli"},{"payload":98,"type":"goog-remb","subtype":null},{"payload":98,"type":"transport-cc","subtype":null},{"payload":98,"type":"ccm","subtype":"fir"},{"payload":98,"type":"nack","subtype":null},{"payload":98,"type":"nack","subtype":"pli"},{"payload":100,"type":"goog-remb","subtype":null},{"payload":100,"type":"transport-cc","subtype":null},{"payload":100,"type":"ccm","subtype":"fir"},{"payload":100,"type":"nack","subtype":null},{"payload":100,"type":"nack","subtype":"pli"},{"payload":102,"type":"goog-remb","subtype":null},{"payload":102,"type":"transport-cc","subtype":null},{"payload":102,"type":"ccm","subtype":"fir"},{"payload":102,"type":"nack","subtype":null},{"payload":102,"type":"nack","subtype":"pli"},{"payload":127,"type":"goog-remb","subtype":null},{"payload":127,"type":"transport-cc","subtype":null},{"payload":127,"type":"ccm","subtype":"fir"},{"payload":127,"type":"nack","subtype":null},{"payload":127,"type":"nack","subtype":"pli"},{"payload":125,"type":"goog-remb","subtype":null},{"payload":125,"type":"transport-cc","subtype":null},{"payload":125,"type":"ccm","subtype":"fir"},{"payload":125,"type":"nack","subtype":null},{"payload":125,"type":"nack","subtype":"pli"},{"payload":108,"type":"goog-remb","subtype":null},{"payload":108,"type":"transport-cc","subtype":null},{"payload":108,"type":"ccm","subtype":"fir"},{"payload":108,"type":"nack","subtype":null},{"payload":108,"type":"nack","subtype":"pli"},{"payload":124,"type":"goog-remb","subtype":null},{"payload":124,"type":"transport-cc","subtype":null},{"payload":124,"type":"ccm","subtype":"fir"},{"payload":124,"type":"nack","subtype":null},{"payload":124,"type":"nack","subtype":"pli"},{"payload":123,"type":"goog-remb","subtype":null},{"payload":123,"type":"transport-cc","subtype":null},{"payload":123,"type":"ccm","subtype":"fir"},{"payload":123,"type":"nack","subtype":null},{"payload":123,"type":"nack","subtype":"pli"}],"ssrcGroups":[{"semantics":"FID","ssrcs":"1184921130 2675549148"}],"ssrcs":[{"id":1184921130,"attribute":"cname","value":"QMcABbRRdb8qCfRw"},{"id":1184921130,"attribute":"msid","value":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl 19aa5442-043c-403e-a9de-e73eea59ebe1"},{"id":1184921130,"attribute":"mslabel","value":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl"},{"id":1184921130,"attribute":"label","value":"19aa5442-043c-403e-a9de-e73eea59ebe1"},{"id":2675549148,"attribute":"cname","value":"QMcABbRRdb8qCfRw"},{"id":2675549148,"attribute":"msid","value":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl 19aa5442-043c-403e-a9de-e73eea59ebe1"},{"id":2675549148,"attribute":"mslabel","value":"KZfI4IWqWP3dQIgwPcK1uiNk5Ty5yxSrrfEl"},{"id":2675549148,"attribute":"label","value":"19aa5442-043c-403e-a9de-e73eea59ebe1"}]}]}'
    
    
    answer = asyncio.run(offer(request))
    print("answer:")
    print(answer)
    
    exit(0)
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--play-from", help="Read the media from a file and sent it."),
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)

