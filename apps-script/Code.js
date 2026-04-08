// Google Apps Script — Job Scraper User Registration
// Deploy as: Web App → Execute as: Me → Access: Anyone
//
// SETUP:
// 1. Go to script.google.com → New Project
// 2. Paste this code
// 3. Replace SPREADSHEET_ID with your Google Sheet ID
// 4. Deploy → New Deployment → Web App → Execute as Me, Access Anyone
// 5. Copy the deployment URL into docs/script.js

var SPREADSHEET_ID = "10P12-tjl556suxe-H0XrstryCaKCy87oZdJaNd4OSPc";
var USERS_SHEET_NAME = "Users";
var MAX_USERS = 5;

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    var name = (data.name || "").trim();
    var keywords = (data.keywords || "").trim();
    var locations = (data.locations || "").trim();
    var sources = (data.sources || "").trim();
    var jobTypes = (data.job_types || "").trim();

    if (!name || !keywords || !locations || !sources || !jobTypes) {
      return jsonResponse({ status: "error", message: "All fields are required." });
    }

    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = getOrCreateUsersSheet(ss);
    var dataRange = sheet.getDataRange();
    var values = dataRange.getValues();

    // Find existing user (skip header row)
    var existingRow = -1;
    var userCount = 0;
    for (var i = 1; i < values.length; i++) {
      if (values[i][0] && values[i][0].toString().trim() !== "") {
        userCount++;
        if (values[i][0].toString().trim().toLowerCase() === name.toLowerCase()) {
          existingRow = i + 1; // 1-indexed for Sheets
        }
      }
    }

    var row = [name, keywords, locations, sources, jobTypes, new Date().toISOString()];

    if (existingRow > 0) {
      // Update existing user
      sheet.getRange(existingRow, 1, 1, 6).setValues([row]);
      return jsonResponse({ status: "ok", message: "Your preferences have been updated!" });
    }

    if (userCount >= MAX_USERS) {
      return jsonResponse({ status: "error", message: "Maximum number of users (" + MAX_USERS + ") reached. Please contact the admin." });
    }

    // Add new user
    sheet.appendRow(row);
    return jsonResponse({ status: "ok", message: "You have been registered! Your jobs will appear in the Google Sheet within 3 days." });

  } catch (err) {
    return jsonResponse({ status: "error", message: "Server error: " + err.toString() });
  }
}

function doGet(e) {
  return jsonResponse({ status: "ok", message: "Job Scraper Registration API is running." });
}

function getOrCreateUsersSheet(ss) {
  var sheet = ss.getSheetByName(USERS_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(USERS_SHEET_NAME);
    sheet.appendRow(["Name", "Keywords", "Locations", "Sources", "Job Types", "Registered At"]);
    sheet.getRange(1, 1, 1, 6).setFontWeight("bold");
  }
  return sheet;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
