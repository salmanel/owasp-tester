import { BrowserRouter, Routes, Route } from "react-router-dom";
import ScanPanel from "./components/ScanPanel";
import ResultsPage from "./pages/Results";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ScanPanel />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
