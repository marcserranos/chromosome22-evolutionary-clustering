import GlobePage from "./pages/GlobePage";
import StarfieldBackground from "./components/StarfieldBackground";

export default function App() {
  return (
    <StarfieldBackground>
      <div className="app">
        <GlobePage />
      </div>
    </StarfieldBackground>
  );
}

