/**
 * Google Apps Script for handling analytics logging from Streamlit app
 * This script receives HTTP POST requests and writes data to Google Sheets
 */

// Configuration - Update these with your actual Google Sheets ID
const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'; // Replace with your actual spreadsheet ID

// Sheet names
const SESSIONS_SHEET_NAME = 'User_Sessions';
const REPORTS_SHEET_NAME = 'Report_Generation';

/**
 * Main function to handle POST requests
 */
function doPost(e) {
  try {
    // Parse the JSON payload
    const requestBody = JSON.parse(e.postData.contents);
    const { action, data } = requestBody;
    
    // Open the spreadsheet
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    
    let result;
    
    switch (action) {
      case 'log_user_session':
        result = logUserSession(spreadsheet, data);
        break;
      case 'log_report_generation':
        result = logReportGeneration(spreadsheet, data);
        break;
      case 'ensure_headers':
        result = ensureHeaders(spreadsheet);
        break;
      default:
        throw new Error(`Unknown action: ${action}`);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error in doPost:', error);
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Ensure both sheets exist with proper headers
 */
function ensureHeaders(spreadsheet) {
  try {
    // User Sessions sheet headers
    const sessionsHeaders = [
      'Timestamp',
      'User Name',
      'Business Email',
      'Company',
      'Session ID',
      'Session Type',
      'User Agent',
      'IP Address',
      'Platform Status'
    ];
    
    // Report Generation sheet headers
    const reportsHeaders = [
      'Timestamp',
      'User Name',
      'Business Email',
      'Target Company',
      'Context Company',
      'Language',
      'Sections Generated',
      'Total Sections',
      'Report Success',
      'Session ID',
      'Generation Time (seconds)',
      'Total Tokens',
      'Input Tokens',
      'Output Tokens',
      'Error Message'
    ];
    
    // Create or get User Sessions sheet
    let sessionsSheet = spreadsheet.getSheetByName(SESSIONS_SHEET_NAME);
    if (!sessionsSheet) {
      sessionsSheet = spreadsheet.insertSheet(SESSIONS_SHEET_NAME);
    }
    
    // Set headers for sessions sheet if empty
    if (sessionsSheet.getLastRow() === 0) {
      sessionsSheet.getRange(1, 1, 1, sessionsHeaders.length).setValues([sessionsHeaders]);
      sessionsSheet.getRange(1, 1, 1, sessionsHeaders.length).setFontWeight('bold');
    }
    
    // Create or get Report Generation sheet
    let reportsSheet = spreadsheet.getSheetByName(REPORTS_SHEET_NAME);
    if (!reportsSheet) {
      reportsSheet = spreadsheet.insertSheet(REPORTS_SHEET_NAME);
    }
    
    // Set headers for reports sheet if empty
    if (reportsSheet.getLastRow() === 0) {
      reportsSheet.getRange(1, 1, 1, reportsHeaders.length).setValues([reportsHeaders]);
      reportsSheet.getRange(1, 1, 1, reportsHeaders.length).setFontWeight('bold');
    }
    
    return { success: true, message: 'Headers ensured for both sheets' };
    
  } catch (error) {
    console.error('Error ensuring headers:', error);
    return { success: false, error: error.toString() };
  }
}

/**
 * Log user session data
 */
function logUserSession(spreadsheet, data) {
  try {
    const sheet = spreadsheet.getSheetByName(SESSIONS_SHEET_NAME);
    if (!sheet) {
      throw new Error(`Sheet ${SESSIONS_SHEET_NAME} not found`);
    }
    
    const row = [
      data.timestamp,
      data.user_name,
      data.business_email,
      data.company,
      data.session_id,
      data.session_type,
      data.user_agent || '-',
      data.ip_address || '-',
      data.platform_status || 'ACTIVE'
    ];
    
    sheet.appendRow(row);
    
    return { success: true, message: 'User session logged successfully' };
    
  } catch (error) {
    console.error('Error logging user session:', error);
    return { success: false, error: error.toString() };
  }
}

/**
 * Log report generation data
 */
function logReportGeneration(spreadsheet, data) {
  try {
    const sheet = spreadsheet.getSheetByName(REPORTS_SHEET_NAME);
    if (!sheet) {
      throw new Error(`Sheet ${REPORTS_SHEET_NAME} not found`);
    }
    
    const row = [
      data.timestamp,
      data.user_name,
      data.business_email,
      data.target_company,
      data.context_company,
      data.language,
      data.sections_generated || '',
      data.total_sections || 0,
      data.report_success || false,
      data.session_id,
      data.generation_time || 0,
      data.total_tokens || 0,
      data.input_tokens || 0,
      data.output_tokens || 0,
      data.error_message || ''
    ];
    
    sheet.appendRow(row);
    
    return { success: true, message: 'Report generation logged successfully' };
    
  } catch (error) {
    console.error('Error logging report generation:', error);
    return { success: false, error: error.toString() };
  }
}

/**
 * Handle GET requests (for testing)
 */
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'Analytics Logger Apps Script is running',
      timestamp: new Date().toISOString(),
      method: 'GET'
    }))
    .setMimeType(ContentService.MimeType.JSON);
} 