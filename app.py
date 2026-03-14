"""Main Flask application for the Resume Processing System."""

from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv
import config
import file_handler
import parser
import deduplication
import result_manager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set specific loggers
logging.getLogger('parser_robust').setLevel(logging.DEBUG)
logging.getLogger('parser').setLevel(logging.DEBUG)

# Global variable to store results
current_results = {
    'candidates': [],
    'errors': [],
    'total_files_processed': 0,
    'duplicates_removed': 0,
    'html_table': ''
}


@app.route('/', methods=['GET'])
def index():
    """Serve the main web interface."""
    try:
        logger.info("Serving main interface")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index: {str(e)}")
        return jsonify({"error": "Failed to load interface"}), 500


@app.route('/upload-zip', methods=['POST'])
def upload_zip():
    """Handle ZIP file upload and processing."""
    global current_results
    
    try:
        logger.info("Processing ZIP upload")
        
        # Check if file is present
        if 'file' not in request.files:
            logger.warning("No file provided in ZIP upload")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Empty filename in ZIP upload")
            return jsonify({"error": "No file selected"}), 400
        
        # Validate ZIP format
        if not file.filename.lower().endswith('.zip'):
            logger.warning(f"Invalid file format: {file.filename}")
            result_manager.log_error(
                "Non-ZIP file uploaded to ZIP endpoint",
                "zip_upload",
                "ValidationError",
                file.filename,
                "warning"
            )
            return jsonify({"error": "File must be a ZIP archive"}), 400
        
        # Extract ZIP in memory
        try:
            extracted_files = file_handler.extract_zip_in_memory(file)
            logger.info(f"Extracted {len(extracted_files)} files from ZIP")
        except Exception as e:
            logger.error(f"Failed to extract ZIP: {str(e)}")
            return jsonify({"error": str(e)}), 400
        
        if not extracted_files:
            logger.warning("No resume files found in ZIP")
            return jsonify({"error": "No PDF or DOCX files found in ZIP"}), 400
        
        # Parse resumes from memory
        try:
            candidates = parser.process_resume_batch_from_bytes(extracted_files)
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            if "spaCy" in str(e) or "en_core_web_sm" in str(e):
                result_manager.log_error(
                    "spaCy model not installed",
                    "zip_upload",
                    "SetupError",
                    "",
                    "error"
                )
                return jsonify({
                    "error": "System not properly configured. Please run: python -m spacy download en_core_web_sm"
                }), 500
            raise
        
        logger.info(f"Parsed {len(candidates)} candidates")
        
        # Filter missing emails
        candidates = deduplication.filter_missing_email(candidates)
        logger.info(f"After email filter: {len(candidates)} candidates")
        
        # Deduplicate
        initial_count = len(candidates)
        candidates = deduplication.deduplicate_candidates(candidates)
        duplicates_removed = initial_count - len(candidates)
        logger.info(f"Removed {duplicates_removed} duplicates")
        
        # Generate HTML table
        html_table = result_manager.generate_html_table(candidates)
        
        # Store results
        current_results = {
            'candidates': candidates,
            'errors': [],
            'total_files_processed': len(extracted_files),
            'duplicates_removed': duplicates_removed,
            'html_table': html_table
        }
        
        logger.info("ZIP processing completed successfully")
        
        return jsonify({
            'success': True,
            'candidates': candidates,
            'html_table': html_table,
            'total_files_processed': len(extracted_files),
            'duplicates_removed': duplicates_removed
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing ZIP: {str(e)}")
        result_manager.log_error(
            str(e),
            "zip_upload",
            "ProcessingError",
            "",
            "error"
        )
        return jsonify({"error": "Failed to process ZIP file"}), 500


@app.route('/upload-drive', methods=['POST'])
def upload_drive():
    """Handle Google Drive public folder link processing."""
    global current_results
    
    try:
        logger.info("Processing Google Drive public folder upload")
        
        # Get folder link from form data
        folder_link = request.form.get('folder_link', '').strip()
        
        if not folder_link:
            logger.warning("No folder link provided")
            return jsonify({"error": "Drive link is required"}), 400
        
        # Extract folder ID
        try:
            folder_id = file_handler.extract_folder_id(folder_link)
            logger.info(f"Extracted folder ID: {folder_id}")
        except ValueError as e:
            logger.warning(f"Invalid Google Drive link: {str(e)}")
            result_manager.log_error(
                str(e),
                "drive_upload",
                "ValidationError",
                folder_link,
                "warning"
            )
            return jsonify({"error": str(e)}), 400
        
        # Download files from public Google Drive folder (no OAuth required)
        try:
            downloaded_files = file_handler.download_from_drive(folder_id, None)
            logger.info(f"Downloaded {len(downloaded_files)} files from Google Drive")
        except Exception as e:
            logger.error(f"Failed to download from Google Drive: {str(e)}")
            result_manager.log_error(
                str(e),
                "drive_upload",
                "GoogleDriveError",
                folder_id,
                "error"
            )
            return jsonify({"error": f"Failed to access Google Drive: {str(e)}"}), 400
        
        if not downloaded_files:
            logger.warning("No files downloaded from Google Drive")
            return jsonify({"error": "No files found in Google Drive folder"}), 400
        
        # Parse resumes from memory
        try:
            candidates = parser.process_resume_batch_from_bytes(downloaded_files)
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            if "spaCy" in str(e) or "en_core_web_sm" in str(e):
                result_manager.log_error(
                    "spaCy model not installed",
                    "drive_upload",
                    "SetupError",
                    "",
                    "error"
                )
                return jsonify({
                    "error": "System not properly configured. Please run: python -m spacy download en_core_web_sm"
                }), 500
            raise
        
        logger.info(f"Parsed {len(candidates)} candidates")
        
        # Filter missing emails
        candidates = deduplication.filter_missing_email(candidates)
        logger.info(f"After email filter: {len(candidates)} candidates")
        
        # Deduplicate
        initial_count = len(candidates)
        candidates = deduplication.deduplicate_candidates(candidates)
        duplicates_removed = initial_count - len(candidates)
        logger.info(f"Removed {duplicates_removed} duplicates")
        
        # Generate HTML table
        html_table = result_manager.generate_html_table(candidates)
        
        # Store results
        current_results = {
            'candidates': candidates,
            'errors': [],
            'total_files_processed': len(downloaded_files),
            'duplicates_removed': duplicates_removed,
            'html_table': html_table
        }
        
        logger.info("Google Drive processing completed successfully")
        
        return jsonify({
            'success': True,
            'candidates': candidates,
            'html_table': html_table,
            'total_files_processed': len(downloaded_files),
            'duplicates_removed': duplicates_removed
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing Google Drive: {str(e)}")
        result_manager.log_error(
            str(e),
            "drive_upload",
            "ProcessingError",
            "",
            "error"
        )
        return jsonify({"error": "Failed to process Google Drive folder"}), 500


@app.route('/upload-single', methods=['POST'])
def upload_single():
    """Handle single resume file upload."""
    global current_results
    
    try:
        logger.info("Processing single file upload")
        
        # Check if file is present
        if 'file' not in request.files:
            logger.warning("No file provided in single upload")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Empty filename in single upload")
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file format
        if not file_handler.validate_file_format(file.filename):
            logger.warning(f"Invalid file format: {file.filename}")
            result_manager.log_error(
                "Unsupported file format",
                "single_upload",
                "ValidationError",
                file.filename,
                "warning"
            )
            return jsonify({"error": "File must be PDF or DOCX format"}), 400
        
        # Read file content into memory
        file.seek(0)
        file_content = file.read()
        
        if not file_content:
            logger.warning("Empty file uploaded")
            return jsonify({"error": "File is empty"}), 400
        
        # Parse resume from memory
        try:
            candidate = parser.parse_resume_from_bytes(file.filename, file_content)
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            error_msg = str(e)
            if "spaCy" in error_msg or "en_core_web_sm" in error_msg:
                result_manager.log_error(
                    "spaCy model not installed",
                    "single_upload",
                    "SetupError",
                    file.filename,
                    "error"
                )
                return jsonify({
                    "error": "System not properly configured. Please run: python -m spacy download en_core_web_sm"
                }), 500
            raise
        
        logger.info(f"Parsed candidate: {candidate.get('name', 'Unknown')}")
        
        # Check if candidate has email
        if not candidate.get('email', '').strip():
            logger.warning("Candidate has no email address")
            result_manager.log_error(
                "Candidate has no email address",
                "single_upload",
                "ValidationError",
                file.filename,
                "warning"
            )
            return jsonify({"error": "Resume must contain an email address"}), 400
        
        # Check for duplicates (in this case, just one candidate)
        candidates = [candidate]
        
        # Generate HTML table
        html_table = result_manager.generate_html_table(candidates)
        
        # Store results
        current_results = {
            'candidates': candidates,
            'errors': [],
            'total_files_processed': 1,
            'duplicates_removed': 0,
            'html_table': html_table
        }
        
        logger.info("Single file processing completed successfully")
        
        return jsonify({
            'success': True,
            'candidates': candidates,
            'html_table': html_table,
            'total_files_processed': 1,
            'duplicates_removed': 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing single file: {str(e)}")
        result_manager.log_error(
            str(e),
            "single_upload",
            "ProcessingError",
            "",
            "error"
        )
        return jsonify({"error": "Failed to process resume file"}), 500


@app.route('/results', methods=['GET'])
def get_results():
    """Return formatted results as JSON."""
    try:
        logger.info("Retrieving results")
        
        if not current_results['candidates']:
            logger.info("No results available yet")
            return jsonify({
                'candidates': [],
                'html_table': '',
                'total_files_processed': 0,
                'duplicates_removed': 0,
                'errors': [],
                'message': 'No results available yet'
            }), 200
        
        return jsonify({
            'candidates': current_results['candidates'],
            'html_table': current_results['html_table'],
            'total_files_processed': current_results['total_files_processed'],
            'duplicates_removed': current_results['duplicates_removed'],
            'errors': current_results['errors']
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({"error": "Failed to retrieve results"}), 500


@app.route('/diagnostic', methods=['POST'])
def diagnostic():
    """Diagnostic endpoint to test parser with uploaded file."""
    try:
        logger.info("Processing diagnostic request")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content
        file.seek(0)
        file_content = file.read()
        
        logger.info(f"Diagnostic: Testing {file.filename} ({len(file_content)} bytes)")
        
        # Test parsing with detailed output
        from parser_robust import (
            extract_text_from_file,
            extract_email,
            extract_phone,
            extract_name
        )
        import tempfile
        from pathlib import Path
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            tmp.write(file_content)
            temp_file = tmp.name
        
        try:
            # Extract text
            text = extract_text_from_file(temp_file)
            
            # Extract fields
            email = extract_email(text)
            phone = extract_phone(text)
            name = extract_name(text)
            
            # Return diagnostic info
            return jsonify({
                'success': True,
                'filename': file.filename,
                'file_size': len(file_content),
                'text_extracted': len(text),
                'text_preview': text[:500] if text else '',
                'email': email,
                'phone': phone,
                'name': name,
                'has_email': bool(email),
                'has_phone': bool(phone),
                'has_name': bool(name)
            }), 200
        finally:
            # Cleanup
            import os
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
    except Exception as e:
        logger.error(f"Diagnostic error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Diagnostic failed: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=config.DEBUG)
