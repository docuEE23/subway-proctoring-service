import React, { useRef, useEffect } from 'react';
import './WebcamViewer.css'; // Import a new CSS file for styling

const WebcamViewer = ({ stream, showAlert }) => { // Added showAlert prop
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className={showAlert ? 'webcam-alert-border' : ''} // Apply class conditionally
      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
    ></video>
  );
};

export default React.memo(WebcamViewer);