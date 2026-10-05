// Token rahasia yang sama dengan yang ada di .env backend Flask (GAS_SECRET_TOKEN)
const SECRET_TOKEN = "ganti_dengan_token_rahasia_yang_sama_di_env";

function doPost(e) {
  try {
    const requestData = JSON.parse(e.postData.contents);
    
    // Verifikasi Token Keamanan
    if (requestData.api_key !== SECRET_TOKEN) {
      return createJsonResponse({ error: "Unauthorized access" }, 401);
    }

    const action = requestData.action;
    const payload = requestData.payload;
    const spreadsheetId = requestData.spreadsheet_id;

    if (!spreadsheetId) {
      return createJsonResponse({ error: "spreadsheet_id is required" }, 400);
    }

    let result = null;

    // Route Actions
    switch (action) {
      case "getAllMembers":
        result = SheetService.getAllMembers(spreadsheetId);
        break;
      case "getStagingMembers":
        result = SheetService.getStagingMembers(spreadsheetId);
        break;
      case "addMemberToStaging":
        result = SheetService.addMemberToStaging(spreadsheetId, payload);
        break;
      case "batchPromoteMembers":
        result = SheetService.batchPromoteMembers(spreadsheetId, payload);
        break;
      case "upgradeMembers":
        result = SheetService.upgradeMembers(spreadsheetId, payload);
        break;
      case "consolidatedPromote":
        result = SheetService.consolidatedPromote(spreadsheetId, payload);
        break;
      case "uploadPhoto":
        result = DriveService.uploadPhoto(payload.base64_data, payload.filename, payload.folder_id, payload.mime_type);
        break;
      case "updateMemberKtaStatus":
        result = SheetService.updateMemberKtaStatus(spreadsheetId, payload.nomor_induk, payload.status);
        break;
      case "getBudgets":
        result = SheetService.getBudgets(spreadsheetId);
        break;
      case "addBudget":
        result = SheetService.addBudget(spreadsheetId, payload);
        break;
      default:
        return createJsonResponse({ error: `Action ${action} not supported` }, 400);
    }

    return createJsonResponse({
      success: true,
      message: "Success",
      data: result
    }, 200);

  } catch (error) {
    return createJsonResponse({ success: false, error: error.message }, 500);
  }
}

function createJsonResponse(data, statusCode) {
  // CATATAN: Apps Script tidak bisa set custom HTTP status code via ContentService
  // Tapi kita bisa sisipkan di dalam payload JSON-nya.
  const response = ContentService.createTextOutput(JSON.stringify(data));
  response.setMimeType(ContentService.MimeType.JSON);
  return response;
}
