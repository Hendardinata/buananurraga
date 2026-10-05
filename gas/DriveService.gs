const DriveService = {
  
  uploadPhoto: function(base64Data, filename, folderId, mimeType) {
    const folder = DriveApp.getFolderById(folderId);
    if (!folder) throw new Error("Folder Drive tidak ditemukan");
    
    // Decode base64
    const blob = Utilities.newBlob(Utilities.base64Decode(base64Data), mimeType, filename);
    const file = folder.createFile(blob);
    
    return {
      file_id: file.getId(),
      file_url: file.getUrl()
    };
  }
  
};
