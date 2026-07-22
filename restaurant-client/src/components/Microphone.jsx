import { useEffect } from "react";
import { useRoomContext } from "@livekit/components-react";


export default function Microphone(){

    const room = useRoomContext();


    useEffect(()=>{

        room.localParticipant
            .setMicrophoneEnabled(true);


    },[]);


    return null;
}