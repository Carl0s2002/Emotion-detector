import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import { socket } from "../../socket";

export default function WebcamDetection() {
  const cam = useRef(null);
  const [ready, setReady] = useState(false);

  
  const [pred, setPred] = useState({ label: "—", conf: 0 });

  
  useEffect(() => {
    const id = setInterval(() => {
      const ok =
        cam.current &&
        cam.current.video &&
        cam.current.video.readyState === 4;
      if (ok) {
        setReady(true);
        clearInterval(id);
      }
    }, 100);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!ready) return;
    if (!socket.connected) {
      socket.on("connect", startLoop);
      return () => socket.off("connect", startLoop);
    }
    startLoop();

    function startLoop() {
      let active = true;
      const tick = () => {
        if (!active) return;
        const jpg = cam.current.getScreenshot();
        if (jpg) socket.emit("frame", jpg);
        setTimeout(tick, 1500);
      };
      tick();
      return () => (active = false);
    }
  }, [ready]);

  
  useEffect(() => {
    const handler = (msg) => setPred(msg);   
    socket.on("prediction", handler);
    return () => socket.off("prediction", handler);
  }, []);

  return (
    <div className="relative inline-block">
      <Webcam
        ref={cam}
        width={320}
        height={240}
        screenshotFormat="image/jpeg"
        className="rounded-lg shadow"
      />

      <span className="absolute bottom-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-sm">
        {pred.label} {Math.round(pred.conf * 100)}%
      </span>
    </div>
  );
}
