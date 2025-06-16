"use client"
import Link from "next/link";
import { useState } from "react";

export default function Page(){
    const [results,setResults] = useState<any[]>([])
    const [prompt, setPrompt] = useState("");
    const [error, setError] = useState<string | null>(null);

    const handleScreen = async () => {
        try {
            setError(null);
            const res = await fetch("http://127.0.0.1:8000/screen-cvs",{
                method:"POST",
                headers:{"Content-Type": "application/json"},
                body: JSON.stringify({ job_prompt: prompt })
            })
            const data = await res.json()
            
            
            if (data.ranked_cvs) {
                setResults(data.ranked_cvs);
                
            } else {
                setError("No results found");
                setResults([]);
            }
        } catch (err) {
            setError("Failed to screen CVs. Please try again.");
            setResults([]);
        }
    }

    return (
        <div className="max-w-xl mx-auto mt-10 space-y-4">
        <textarea
          className="w-full border p-2 rounded"
          placeholder="Paste your job description here"
          rows={6}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button
          onClick={handleScreen}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Screen CVs
        </button>
  
        {error && (
          <div className="text-red-500 mt-4">
            {error}
          </div>
        )}

        <div className="mt-6 space-y-4">
          {results && results.length > 0 ? (
            results.map((cv, i) => (
              <div key={i} className="p-4 border rounded shadow">
                <h3 className="font-bold">{cv.filename}</h3>
                <pre className="text-sm whitespace-pre-wrap">{cv.score_and_reason}</pre>
              </div>
            ))
          ) : (
            <div className="text-gray-500 text-center">
              No CVs to display. Please upload some CVs first.
            </div>
          )}
        </div>
      </div>
    )
}