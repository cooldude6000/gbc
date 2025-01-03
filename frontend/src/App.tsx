import "./App.css";
import { MediaRecorder } from "./features/mediaRecorder/components/MediaRecorder";

function App() {
  const config = {
    webcam: { video: true, audio: true },
    screen: { video: true, audio: true },
  };

  return (
    <div className="app-container">
      <h1>Screen Recorder</h1>
      <MediaRecorder config={config} />
    </div>
  );
}

export default App;
