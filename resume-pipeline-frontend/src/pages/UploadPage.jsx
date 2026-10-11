import { useState } from 'react'
import reactLogo from '../assets/react.svg'
import viteLogo from '../assets/vite.svg'
import heroImg from '../assets/hero.png'
import '../App.css'
import { Link } from 'react-router-dom'

// Child components
import ResumeUploadForm from '../components/forms/ResumeUploadForm'

export default function UploadPage() {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("Please select file");
  const [isUploading, setIsUploading] = useState(false);
  // const [url, setUrl] = useState("");

  async function checkAPI() {
    try {
      const response = await fetch("http://localhost:8080/uploads/test");
      const data = await response.text();
      setMessage(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function upload(){
    // !!! to do: check upload status to avoid multiple uploads at the same time


    if (!file) {
      setUploadMessage("No file selected!")
      return
    }

    setIsUploading(true)
    
    //Catch error if file is not PDF 
    let map
    try {
      map = await getPresigned();
    } catch (error) {
      setUploadMessage(error.message);
      setIsUploading(false)
      return
    }

    // for testing purposes -> output the response of getting presigned URL
    setUploadInfo(map)

    try {
      const uploadResponse = await fetch(map.uploadUrl, {
        method: "PUT",
        headers: {
          "Content-Type": file.type,
        },
        body: file,
      });
      setUploadMessage("Upload Success! Parsing...")
    } catch (error) {
      setUploadMessage(error.message)
      setIsUploading(false)
      return
    }

    let parsedResponseJSON;
    try{
      const parsedResponse = await fetch(`http://localhost:8080/uploads/parse/${map.uploadId}`, {
      method: "POST",
      });
      parsedResponseJSON = await parsedResponse.json()
      const parsedDisplay = JSON.stringify(parsedResponseJSON, null, 2)
      setUploadMessage(`Parse Success! Saving...\n${parsedDisplay}`)
    } catch (error) {
      setUploadMessage(error.message)
      setIsUploading(false)
      return
    }
    
    try {
      const saveResponse = await fetch(`http://localhost:8080/uploads/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsedResponseJSON)
        });
      
      const savedInfo = await saveResponse.text();

      // if (savedInfo.responseMessage === "DUPLICATE") {
      //   retu
      // }

      setUploadMessage(`Save Success! \n${savedInfo}`)
    } catch (error) {
      setUploadMessage(error.message)
      setIsUploading(false)
      return
    }

    setFile(null)
    setIsUploading(false)

  }

  /*
  * Gets the presigned URL from the server
  * 
  * @returns the response as a json object from server containing:
  * - uploadUrl
  * - objectKey
  * - uploadId
  */
  async function getPresigned(){
    //File should be pdf
    if (file.type !== "application/pdf") {
      throw new Error("File must be a PDF");
    }

    const response = await fetch("http://localhost:8080/uploads/presign", {
      method: "POST",
      headers: {
      "Content-Type": "application/json",
      },
      body: JSON.stringify({
      filename: file.name,
      })
    })

    if (!response.ok) {
      console.log(await response.text());
    }

    const res = await response.json()
    return res
  }

  return (
    <>
      <button onClick={checkAPI}>
        checkAPI
      </button>

      <h2>{message}</h2>

      <h1> Upload your file here </h1>
      <ResumeUploadForm upload={upload} isUploading={isUploading} setFile={setFile}/>

      {(isUploading) ? <>
        <p>Please wait...</p>
      </>:<>
      
      </>}

      <h2 style={{ whiteSpace: "pre-wrap" }}>{uploadMessage}</h2>

      <h2>{file?.name}</h2>
      <h2>{file?.type}</h2>
      <h2>{uploadInfo?.objectKey}</h2>
      <h2>{uploadInfo?.uploadId}</h2>
    </>
  )
}
