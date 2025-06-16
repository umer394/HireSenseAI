"use client"
import { useState } from "react"

export default function UploadFile(){
    const [file,setFile] = useState<File | null>(null)
    const [jobTitle ,setJobTitle] = useState("")

    const handleUpload = async () => {
        if (!file || !jobTitle) return alert("Please select file and job title");
        const formData = new FormData();
        formData.append("file",file)
        formData.append("job_title",jobTitle)

        const res = await fetch("http://127.0.0.1:8000/upload-cv",{
            method:"POST",
            body: formData
        })

        const data = await res.json();
        alert(`CV Uploaded: ${data.id}`)
    }

    return(
        <div className="max-w-xl mx-auto mt-10 space-y-4">
      <input
        type="text"
        placeholder="Enter Job Title"
        className="w-full border p-2 rounded"
        onChange={(e) => setJobTitle(e.target.value)}
      />
      <input
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Upload CV
      </button>
    </div>
  );
}
  