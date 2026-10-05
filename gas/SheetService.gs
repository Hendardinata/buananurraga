const SheetService = {
  
  getAllMembers: function(spreadsheetId) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("DATA PUSAT");
    
    if (!sheet) throw new Error("Sheet 'DATA PUSAT' tidak ditemukan");
    
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1);
    
    const members = rows.map(row => {
      let member = {};
      headers.forEach((header, index) => {
        member[header] = row[index];
      });
      return member;
    });
    
    return members;
  },

  getStagingMembers: function(spreadsheetId) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("DATA MENTAH");
    
    if (!sheet) throw new Error("Sheet 'DATA MENTAH' tidak ditemukan");
    
    const data = sheet.getDataRange().getValues();
    if (data.length <= 1) return []; // Only headers or empty
    
    const headers = data[0];
    const rows = data.slice(1);
    
    const members = rows.map((row, index) => {
      let member = { _rowIndex: index + 2 }; // Store 1-based sheet row index for potential updates/deletes
      headers.forEach((header, colIndex) => {
        member[header] = row[colIndex];
      });
      return member;
    });
    
    return members;
  },

  batchPromoteMembers: function(spreadsheetId, payload) {
    // payload: { event_date: "2026-10-04", location: {desa, kecamatan, kabupaten}, promotions: [...] }
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const pusatSheet = ss.getSheetByName("DATA PUSAT");
    const mentahSheet = ss.getSheetByName("DATA MENTAH");
    const rekapSheet = ss.getSheetByName("REKAP DATA"); // Optional update if needed
    
    if (!pusatSheet || !mentahSheet) throw new Error("Sheet DATA PUSAT atau DATA MENTAH tidak ditemukan");

    // 1. Prepare data for DATA PUSAT
    const rowsToAdd = payload.promotions.map(promo => {
      return [
        payload.event_date || "", // 1: TANGGAL SAH
        promo.nomor_induk || "",  // 2: NOMOR INDUK
        promo.cabang || "",       // 3: CABANG
        promo.nama_lengkap || "", // 4: NAMA LENGKAP
        promo.ttl || "",          // 5: TEMPAT TANGGAL LAHIR
        promo.jenis_kelamin || "",// 6: JENIS KELAMIN
        promo.dusun || "",        // 7: DUSUN/LINGKUNGAN
        promo.desa || "",         // 8: DESA/KELURAHAN
        promo.kecamatan || "",    // 9: KECAMATAN
        payload.location ? (payload.location.kabupaten || "") : "", // 10: KABUPATEN/KOTA
        promo.whatsapp || "",     // 11: NOMOR WHATSAAP
        promo.nomor_darurat || "",// 12: NOMOR DARURAT
        payload.event_date || "", // 13: HIJAU
        "-",                      // 14: BIRU
        "-",                      // 15: COKELAT
        "-",                      // 16: HITAM COKELAT
        "-",                      // 17: HITAM ORANGE
        "-",                      // 18: GURU
        "-",                      // 19: GURU BESAR
        null,                     // 20: KTA (null agar lolos validasi dropdown jika belum punya)
        promo.new_level || "HIJAU"// 21: SABUK
      ];
    });

    if (rowsToAdd.length > 0) {
      const addedRange = pusatSheet.getRange(pusatSheet.getLastRow() + 1, 1, rowsToAdd.length, rowsToAdd[0].length);
      addedRange.setValues(rowsToAdd);
      
      // Fix date formatting for TANGGAL SAH (Column A) and HIJAU (Column M) in DATA PUSAT to be consistent
      pusatSheet.getRange(pusatSheet.getLastRow() - rowsToAdd.length + 1, 1, rowsToAdd.length, 1).setNumberFormat("dd-mm-yyyy");
      pusatSheet.getRange(pusatSheet.getLastRow() - rowsToAdd.length + 1, 13, rowsToAdd.length, 1).setNumberFormat("dd-mm-yyyy");
      
      // 1.5 Prepare data for ARSIP KENAIKAN TINGKAT
      const arsipSheet = ss.getSheetByName("ARSIP KENAIKAN TINGKAT");
      if (arsipSheet) {
        let hijauCount = 0, biruCount = 0, cokelatCount = 0, hitamCokelatCount = 0;
        let hitamOrangeCount = 0, guruCount = 0, guruBesarCount = 0;
        
        const arsipRows = payload.promotions.map((promo, index) => {
          let row = [
            payload.event_date || "", // 1: ANGKATAN
            index + 1,                // 2: URUTAN
            "", "", "", "", "", "", "", "" // 3-10 placeholders
          ];
          
          let level = (promo.new_level || "HIJAU").toUpperCase();
          if (level === "HIJAU") { row[2] = promo.nama_lengkap; hijauCount++; }
          else if (level === "BIRU") { row[3] = promo.nama_lengkap; biruCount++; }
          else if (level === "COKELAT") { row[4] = promo.nama_lengkap; cokelatCount++; }
          else if (level === "HITAM COKELAT") { row[5] = promo.nama_lengkap; hitamCokelatCount++; }
          else if (level === "HITAM ORANGE") { row[6] = promo.nama_lengkap; hitamOrangeCount++; }
          else if (level === "GURU") { row[7] = promo.nama_lengkap; guruCount++; }
          else if (level === "GURU BESAR") { row[8] = promo.nama_lengkap; guruBesarCount++; }
          
          return row;
        });
        
        // Add TOTAL row
        arsipRows.push([
          "", // ANGKATAN
          "TOTAL", // URUTAN
          hijauCount || "",
          biruCount || "",
          cokelatCount || "",
          hitamCokelatCount || "",
          hitamOrangeCount || "",
          guruCount || "",
          guruBesarCount || "",
          payload.promotions.length // TOTAL PESERTA
        ]);
        
        const startRowArsip = arsipSheet.getLastRow() + 1;
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length, 10).setValues(arsipRows);
        
        // Format dates in ARSIP (Column A)
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length - 1, 1).setNumberFormat("dd/MM/yyyy");
        
        // Apply yellow background to the TOTAL row (last row of the inserted batch)
        const totalRowRange = arsipSheet.getRange(startRowArsip + arsipRows.length - 1, 1, 1, 10);
        totalRowRange.setBackground("#FFFF00"); // Yellow
        totalRowRange.setFontWeight("bold");
      }
      
      // 1.6 Prepare data for LOKASI DAN JUMLAH PESERTA NAIK
      const lokasiSheet = ss.getSheetByName("LOKASI DAN JUMLAH PESERTA NAIK "); // Note the space at the end, from PRD
      if (lokasiSheet) {
        let hijauCount = 0, biruCount = 0, cokelatCount = 0, hitamCokelatCount = 0;
        let hitamOrangeCount = 0, guruCount = 0, guruBesarCount = 0;
        
        payload.promotions.forEach(promo => {
          let level = (promo.new_level || "HIJAU").toUpperCase();
          if (level === "HIJAU") hijauCount++;
          else if (level === "BIRU") biruCount++;
          else if (level === "COKELAT") cokelatCount++;
          else if (level === "HITAM COKELAT") hitamCokelatCount++;
          else if (level === "HITAM ORANGE") hitamOrangeCount++;
          else if (level === "GURU") guruCount++;
          else if (level === "GURU BESAR") guruBesarCount++;
        });
        
        let lastNo = 0;
        const lastRowLokasi = lokasiSheet.getLastRow();
        if (lastRowLokasi > 1) {
          lastNo = Number(lokasiSheet.getRange(lastRowLokasi, 1).getValue()) || 0;
        }
        
        lokasiSheet.appendRow([
          lastNo + 1,
          payload.event_date || "",
          payload.location ? payload.location.desa || "" : "",
          payload.location ? payload.location.kecamatan || "" : "",
          payload.location ? payload.location.kabupaten || "" : "",
          hijauCount || "",
          biruCount || "",
          cokelatCount || "",
          hitamCokelatCount || "",
          hitamOrangeCount || "",
          guruCount || "",
          guruBesarCount || "",
          payload.promotions.length
        ]);
      }
    }
    
    // 2. Clear staging data that has been promoted (Simulated by clearing all for now, or match by name)
    // For now, let's just clear the "DATA MENTAH" completely except headers because we process all of it.
    const lastRow = mentahSheet.getLastRow();
    if (lastRow > 1) {
      mentahSheet.getRange(2, 1, lastRow - 1, mentahSheet.getLastColumn()).clearContent();
    }
    
    return { success: true, count: rowsToAdd.length, message: "Berhasil mengesahkan " + rowsToAdd.length + " anggota" };
  },

  addMemberToStaging: function(spreadsheetId, memberData) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("DATA MENTAH");
    
    if (!sheet) throw new Error("Sheet 'DATA MENTAH' tidak ditemukan");
    
    // Asumsi urutan kolom di DATA MENTAH:
    // TANGGAL NAIK, URUTAN, CABANG, NAMA LENGKAP, TEMPAT TANGGAL LAHIR, JENIS KELAMIN, 
    // DUSUN/LINGKUNGAN, DESA/KELURAHAN, KECAMATAN, NOMOR WHATSAAP, NOMOR DARURAT
    
    sheet.appendRow([
      memberData.tanggal_naik || "",
      memberData.urutan || "",
      memberData.cabang || "",
      memberData.nama_lengkap || "",
      memberData.ttl || "",
      memberData.jenis_kelamin || "",
      memberData.dusun || "",
      memberData.desa || "",
      memberData.kecamatan || "",
      memberData.whatsapp || "",
      memberData.nomor_darurat || ""
    ]);
    
    return { status: "Member added to staging" };
  },

  updateMemberKtaStatus: function(spreadsheetId, nomorInduk, ktaStatus) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("DATA PUSAT");
    if (!sheet) throw new Error("Sheet 'DATA PUSAT' tidak ditemukan");

    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const noIndukIndex = headers.indexOf("NOMOR INDUK");
    const ktaIndex = headers.indexOf("KTA");

    if (noIndukIndex === -1 || ktaIndex === -1) {
      throw new Error("Kolom 'NOMOR INDUK' atau 'KTA' tidak ditemukan di DATA PUSAT");
    }

    const searchTarget = String(nomorInduk).trim().toLowerCase();
    for (let i = 1; i < data.length; i++) {
      if (String(data[i][noIndukIndex]).trim().toLowerCase() === searchTarget) {
        sheet.getRange(i + 1, ktaIndex + 1).setValue(ktaStatus || "PUNYA");
        return { updated: true, nomor_induk: nomorInduk, status: ktaStatus || "PUNYA" };
      }
    }
    throw new Error("Anggota dengan Nomor Induk " + nomorInduk + " tidak ditemukan");
  },

  getBudgets: function(spreadsheetId) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("TRANSAKSI ANGGARAN");
    if (!sheet) throw new Error("Sheet 'TRANSAKSI ANGGARAN' tidak ditemukan. Harap buat sheet baru dengan nama ini.");
    
    const data = sheet.getDataRange().getValues();
    if (data.length <= 1) return []; // Only headers
    
    const headers = data[0];
    const rows = data.slice(1);
    
    return rows.map((row) => {
      let budget = {};
      headers.forEach((header, colIndex) => {
        budget[header] = row[colIndex];
      });
      return budget;
    });
  },

  addBudget: function(spreadsheetId, payload) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName("TRANSAKSI ANGGARAN");
    if (!sheet) throw new Error("Sheet 'TRANSAKSI ANGGARAN' tidak ditemukan. Harap buat sheet baru dengan nama ini.");
    
    // Expected structure:
    // TANGGAL, KETERANGAN, JENIS (PEMASUKAN/PENGELUARAN), NOMINAL, SALDO, CABANG (Optional)
    const lastRow = sheet.getLastRow();
    let lastSaldo = 0;
    if (lastRow > 1) {
       const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
       const saldoIndex = headers.indexOf("SALDO");
       if (saldoIndex !== -1) {
         lastSaldo = parseFloat(sheet.getRange(lastRow, saldoIndex + 1).getValue()) || 0;
       }
    }
    
    const isIncome = payload.jenis && payload.jenis.toUpperCase() === 'PEMASUKAN';
    const nominal = parseFloat(payload.nominal) || 0;
    const currentSaldo = isIncome ? lastSaldo + nominal : lastSaldo - nominal;

    sheet.appendRow([
      payload.tanggal || new Date(),
      payload.keterangan || "",
      payload.jenis || "",
      nominal,
      currentSaldo,
      payload.cabang || "PUSAT"
    ]);

    return { status: "Budget added successfully", new_saldo: currentSaldo };
  },

  upgradeMembers: function(spreadsheetId, payload) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const pusatSheet = ss.getSheetByName("DATA PUSAT");
    if (!pusatSheet) throw new Error("Sheet DATA PUSAT tidak ditemukan");

    // payload: { event_date: "2026-10-04", location: {desa, kecamatan, kabupaten}, members: [{nomor_induk, new_level, nama_lengkap}, ...] }
    
    const data = pusatSheet.getDataRange().getValues();
    const headers = data[0];
    const noIndukIndex = headers.indexOf("NOMOR INDUK");
    const sabukIndex = headers.indexOf("SABUK");
    const cabangIndex = headers.indexOf("CABANG");
    
    const beltColumns = {
      "HIJAU": headers.indexOf("HIJAU"),
      "BIRU": headers.indexOf("BIRU"),
      "COKELAT": headers.indexOf("COKELAT"),
      "HITAM COKELAT": headers.indexOf("HITAM COKELAT"),
      "HITAM ORANGE": headers.indexOf("HITAM ORANGE"),
      "GURU": headers.indexOf("GURU"),
      "GURU BESAR": headers.indexOf("GURU BESAR")
    };

    if (noIndukIndex === -1 || sabukIndex === -1) throw new Error("Kolom NOMOR INDUK atau SABUK tidak ditemukan");

    let updatedCount = 0;
    
    const promotionsByLevel = {
      "HIJAU": [], "BIRU": [], "COKELAT": [], "HITAM COKELAT": [], 
      "HITAM ORANGE": [], "GURU": [], "GURU BESAR": []
    };

    const targetMembersMap = {};
    payload.members.forEach(m => {
      targetMembersMap[String(m.nomor_induk).trim().toLowerCase()] = m;
    });

    for (let i = 1; i < data.length; i++) {
      const nip = String(data[i][noIndukIndex]).trim().toLowerCase();
      if (targetMembersMap[nip]) {
        const promo = targetMembersMap[nip];
        const newLevel = (promo.new_level || "").toUpperCase();
        
        data[i][sabukIndex] = newLevel;
        
        const dateColIdx = beltColumns[newLevel];
        if (dateColIdx !== -1) {
          data[i][dateColIdx] = payload.event_date || "";
        }
        
        if (promotionsByLevel[newLevel]) {
          promotionsByLevel[newLevel].push({
             nama_lengkap: data[i][headers.indexOf("NAMA LENGKAP")],
             cabang: data[i][cabangIndex]
          });
        }
        
        updatedCount++;
      }
    }

    if (updatedCount > 0) {
      pusatSheet.getRange(1, 1, data.length, data[0].length).setValues(data);
      
      const arsipSheet = ss.getSheetByName("ARSIP KENAIKAN TINGKAT");
      if (arsipSheet) {
        const arsipRows = [];
        
        payload.members.forEach((promo, index) => {
          let row = [
            payload.event_date || "", // 1: ANGKATAN
            index + 1,                // 2: URUTAN
            "", "", "", "", "", "", "", "" // 3-10 placeholders
          ];
          
          let level = (promo.new_level || "HIJAU").toUpperCase();
          if (level === "HIJAU") { row[2] = promo.nama_lengkap; }
          else if (level === "BIRU") { row[3] = promo.nama_lengkap; }
          else if (level === "COKELAT") { row[4] = promo.nama_lengkap; }
          else if (level === "HITAM COKELAT") { row[5] = promo.nama_lengkap; }
          else if (level === "HITAM ORANGE") { row[6] = promo.nama_lengkap; }
          else if (level === "GURU") { row[7] = promo.nama_lengkap; }
          else if (level === "GURU BESAR") { row[8] = promo.nama_lengkap; }
          
          arsipRows.push(row);
        });
        
        arsipRows.push([
          "", // ANGKATAN
          "TOTAL", // URUTAN
          promotionsByLevel["HIJAU"].length || "",
          promotionsByLevel["BIRU"].length || "",
          promotionsByLevel["COKELAT"].length || "",
          promotionsByLevel["HITAM COKELAT"].length || "",
          promotionsByLevel["HITAM ORANGE"].length || "",
          promotionsByLevel["GURU"].length || "",
          promotionsByLevel["GURU BESAR"].length || "",
          payload.members.length // TOTAL PESERTA
        ]);
        
        const startRowArsip = arsipSheet.getLastRow() + 1;
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length, 10).setValues(arsipRows);
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length - 1, 1).setNumberFormat("dd/MM/yyyy");
        
        const totalRowRange = arsipSheet.getRange(startRowArsip + arsipRows.length - 1, 1, 1, 10);
        totalRowRange.setBackground("#FFFF00");
        totalRowRange.setFontWeight("bold");
      }
      
      const lokasiSheet = ss.getSheetByName("LOKASI DAN JUMLAH PESERTA NAIK ");
      if (lokasiSheet) {
        let lastNo = 0;
        const lastRowLokasi = lokasiSheet.getLastRow();
        if (lastRowLokasi > 1) {
          lastNo = Number(lokasiSheet.getRange(lastRowLokasi, 1).getValue()) || 0;
        }
        
        lokasiSheet.appendRow([
          lastNo + 1,
          payload.event_date || "",
          payload.location ? payload.location.desa || "" : "",
          payload.location ? payload.location.kecamatan || "" : "",
          payload.location ? payload.location.kabupaten || "" : "",
          promotionsByLevel["HIJAU"].length || "",
          promotionsByLevel["BIRU"].length || "",
          promotionsByLevel["COKELAT"].length || "",
          promotionsByLevel["HITAM COKELAT"].length || "",
          promotionsByLevel["HITAM ORANGE"].length || "",
          promotionsByLevel["GURU"].length || "",
          promotionsByLevel["GURU BESAR"].length || "",
          payload.members.length
        ]);
      }
    }

    return { success: true, count: updatedCount, message: "Berhasil menaikkan tingkat " + updatedCount + " anggota" };
  },

  consolidatedPromote: function(spreadsheetId, payload) {
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const pusatSheet = ss.getSheetByName("DATA PUSAT");
    const mentahSheet = ss.getSheetByName("DATA MENTAH");
    
    if (!pusatSheet || !mentahSheet) throw new Error("Sheet DATA PUSAT atau DATA MENTAH tidak ditemukan");

    // payload: { event_date, location, new_members: [], upgrade_members: [] }
    const newMembers = payload.new_members || [];
    const upgradeMembers = payload.upgrade_members || [];
    
    const promotionsByLevel = {
      "HIJAU": [], "BIRU": [], "COKELAT": [], "HITAM COKELAT": [], 
      "HITAM ORANGE": [], "GURU": [], "GURU BESAR": []
    };
    
    // 1. Process New Members
    let rowsToAdd = [];
    if (newMembers.length > 0) {
      rowsToAdd = newMembers.map(promo => {
        const level = (promo.new_level || "HIJAU").toUpperCase();
        if (promotionsByLevel[level]) {
          promotionsByLevel[level].push({ nama_lengkap: promo.nama_lengkap, cabang: promo.cabang });
        }
        return [
          payload.event_date || "", // 1: TANGGAL SAH
          promo.nomor_induk || "",  // 2: NOMOR INDUK
          promo.cabang || "",       // 3: CABANG
          promo.nama_lengkap || "", // 4: NAMA LENGKAP
          promo.ttl || "",          // 5: TEMPAT TANGGAL LAHIR
          promo.jenis_kelamin || "",// 6: JENIS KELAMIN
          promo.dusun || "",        // 7: DUSUN/LINGKUNGAN
          promo.desa || "",         // 8: DESA/KELURAHAN
          promo.kecamatan || "",    // 9: KECAMATAN
          payload.location ? (payload.location.kabupaten || "") : "", // 10: KABUPATEN/KOTA
          promo.whatsapp || "",     // 11: NOMOR WHATSAAP
          promo.nomor_darurat || "",// 12: NOMOR DARURAT
          payload.event_date || "", // 13: HIJAU
          "-",                      // 14: BIRU
          "-",                      // 15: COKELAT
          "-",                      // 16: HITAM COKELAT
          "-",                      // 17: HITAM ORANGE
          "-",                      // 18: GURU
          "-",                      // 19: GURU BESAR
          null,                     // 20: KTA
          level                     // 21: SABUK
        ];
      });
      
      const addedRange = pusatSheet.getRange(pusatSheet.getLastRow() + 1, 1, rowsToAdd.length, rowsToAdd[0].length);
      addedRange.setValues(rowsToAdd);
      pusatSheet.getRange(pusatSheet.getLastRow() - rowsToAdd.length + 1, 1, rowsToAdd.length, 1).setNumberFormat("dd-mm-yyyy");
      pusatSheet.getRange(pusatSheet.getLastRow() - rowsToAdd.length + 1, 13, rowsToAdd.length, 1).setNumberFormat("dd-mm-yyyy");
      
      const lastRowMentah = mentahSheet.getLastRow();
      if (lastRowMentah > 1) {
        mentahSheet.getRange(2, 1, lastRowMentah - 1, mentahSheet.getLastColumn()).clearContent();
      }
    }
    
    // 2. Process Upgrades
    let updatedCount = 0;
    if (upgradeMembers.length > 0) {
      const data = pusatSheet.getDataRange().getValues();
      const headers = data[0];
      const noIndukIndex = headers.indexOf("NOMOR INDUK");
      const sabukIndex = headers.indexOf("SABUK");
      const cabangIndex = headers.indexOf("CABANG");
      
      const beltColumns = {
        "HIJAU": headers.indexOf("HIJAU"), "BIRU": headers.indexOf("BIRU"), "COKELAT": headers.indexOf("COKELAT"),
        "HITAM COKELAT": headers.indexOf("HITAM COKELAT"), "HITAM ORANGE": headers.indexOf("HITAM ORANGE"),
        "GURU": headers.indexOf("GURU"), "GURU BESAR": headers.indexOf("GURU BESAR")
      };
      
      const targetMembersMap = {};
      upgradeMembers.forEach(m => {
        targetMembersMap[String(m.nomor_induk).trim().toLowerCase()] = m;
      });
      
      for (let i = 1; i < data.length; i++) {
        const nip = String(data[i][noIndukIndex]).trim().toLowerCase();
        if (targetMembersMap[nip]) {
          const promo = targetMembersMap[nip];
          const newLevel = (promo.new_level || "").toUpperCase();
          data[i][sabukIndex] = newLevel;
          const dateColIdx = beltColumns[newLevel];
          if (dateColIdx !== -1) {
            data[i][dateColIdx] = payload.event_date || "";
          }
          if (promotionsByLevel[newLevel]) {
            promotionsByLevel[newLevel].push({
               nama_lengkap: data[i][headers.indexOf("NAMA LENGKAP")],
               cabang: data[i][cabangIndex]
            });
          }
          updatedCount++;
        }
      }
      
      if (updatedCount > 0) {
        pusatSheet.getRange(1, 1, data.length, data[0].length).setValues(data);
      }
    }
    
    // 3. Consolidated ARSIP & LOKASI
    const totalProcessed = newMembers.length + updatedCount;
    if (totalProcessed > 0) {
      const arsipSheet = ss.getSheetByName("ARSIP KENAIKAN TINGKAT");
      if (arsipSheet) {
        const arsipRows = [];
        let combinedMembers = [];
        
        // Combine new and upgraded to create rows sequentially
        newMembers.forEach(m => combinedMembers.push({ nama_lengkap: m.nama_lengkap, new_level: m.new_level || "HIJAU" }));
        upgradeMembers.forEach(m => combinedMembers.push({ nama_lengkap: m.nama_lengkap, new_level: m.new_level }));
        
        combinedMembers.forEach((promo, index) => {
          let row = [
            payload.event_date || "", index + 1, "", "", "", "", "", "", "", ""
          ];
          let level = (promo.new_level || "HIJAU").toUpperCase();
          if (level === "HIJAU") { row[2] = promo.nama_lengkap; }
          else if (level === "BIRU") { row[3] = promo.nama_lengkap; }
          else if (level === "COKELAT") { row[4] = promo.nama_lengkap; }
          else if (level === "HITAM COKELAT") { row[5] = promo.nama_lengkap; }
          else if (level === "HITAM ORANGE") { row[6] = promo.nama_lengkap; }
          else if (level === "GURU") { row[7] = promo.nama_lengkap; }
          else if (level === "GURU BESAR") { row[8] = promo.nama_lengkap; }
          arsipRows.push(row);
        });
        
        arsipRows.push([
          "", "TOTAL",
          promotionsByLevel["HIJAU"].length || "", promotionsByLevel["BIRU"].length || "",
          promotionsByLevel["COKELAT"].length || "", promotionsByLevel["HITAM COKELAT"].length || "",
          promotionsByLevel["HITAM ORANGE"].length || "", promotionsByLevel["GURU"].length || "",
          promotionsByLevel["GURU BESAR"].length || "", totalProcessed
        ]);
        
        const startRowArsip = arsipSheet.getLastRow() + 1;
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length, 10).setValues(arsipRows);
        arsipSheet.getRange(startRowArsip, 1, arsipRows.length - 1, 1).setNumberFormat("dd/MM/yyyy");
        const totalRowRange = arsipSheet.getRange(startRowArsip + arsipRows.length - 1, 1, 1, 10);
        totalRowRange.setBackground("#FFFF00").setFontWeight("bold");
      }
      
      const lokasiSheet = ss.getSheetByName("LOKASI DAN JUMLAH PESERTA NAIK ");
      if (lokasiSheet) {
        let lastNo = 0;
        const lastRowLokasi = lokasiSheet.getLastRow();
        if (lastRowLokasi > 1) {
          lastNo = Number(lokasiSheet.getRange(lastRowLokasi, 1).getValue()) || 0;
        }
        lokasiSheet.appendRow([
          lastNo + 1,
          payload.event_date || "",
          payload.location ? payload.location.desa || "" : "",
          payload.location ? payload.location.kecamatan || "" : "",
          payload.location ? payload.location.kabupaten || "" : "",
          promotionsByLevel["HIJAU"].length || "",
          promotionsByLevel["BIRU"].length || "",
          promotionsByLevel["COKELAT"].length || "",
          promotionsByLevel["HITAM COKELAT"].length || "",
          promotionsByLevel["HITAM ORANGE"].length || "",
          promotionsByLevel["GURU"].length || "",
          promotionsByLevel["GURU BESAR"].length || "",
          totalProcessed
        ]);
      }
    }
    
    return { success: true, count: totalProcessed, message: "Berhasil memproses " + totalProcessed + " anggota" };
  }
};
