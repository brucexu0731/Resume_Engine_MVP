import Button from '@mui/material/Button';
import SaveIcon from '@mui/icons-material/Save';

export default function ResumeUploadForm(props) {
    return <>
        <form>
            <input id="fileInput" type="file" onChange={(e) => props.setFile(e.target.files[0])}/>
            <Button 
                type="button" 
                variant="contained"
                color="secondary"
                onClick={props.upload}
                loading={props.isUploading}
                loadingPosition="start"
                startIcon={<SaveIcon />}
            >
                {props.isUploading ? "Uploading..." : "Upload"}
            </Button>
        </form>
    </>
}