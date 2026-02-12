import { useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [occasion, setOccasion] = useState("Casual");
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("occasion", occasion);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/user/upload",
        formData
      );

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("Upload failed. Check backend.");
    }
  };

  return (
    <div className="p-10">
      <h2 className="text-2xl font-bold mb-4">
        Upload Your Photo
      </h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <br />

      <select
        value={occasion}
        onChange={(e) => setOccasion(e.target.value)}
        className="border p-2 mb-4"
      >
        <option value="Casual">Casual</option>
        <option value="Office">Office</option>
        <option value="Wedding">Wedding</option>
      </select>

      <br />

      <button
        onClick={handleUpload}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Upload
      </button>

      {result && (
        <div className="mt-6">
          <h3 className="font-bold">Body Analysis</h3>
          <p>Shoulder Width: {result.shoulder_width}</p>
          <p>Hip Width: {result.hip_width}</p>
          <p>Body Type: {result.body_type}</p>
        </div>
      )}
    </div>
  );
}
