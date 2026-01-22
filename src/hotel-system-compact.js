function สร้างระบบโรงแรมแบบกระชับ() {
  const ss = SpreadsheetApp.create('Hotel Management System');
  
  function สร้างชีต(ชื่อ, หัวตาราง) {
    const sheet = ss.insertSheet(ชื่อ);
    sheet.getRange(1, 1, 1, หัวตาราง.length).setValues([หัวตาราง]);
    sheet.setFrozenRows(1);
    sheet.getRange(1,1,1,หัวตาราง.length)
      .setFontWeight('bold')
      .setBackground('#E3F2FD');
    return sheet;
  }

  // 1. ข้อมูลหลัก (Master Data)
  สร้างชีต('ลูกค้า_Customers', [
    'Customer_ID','ชื่อ','เบอร์โทร','อีเมล','ที่อยู่','ประเภท','วันที่สมัคร','สถานะ'
  ]);
  
  สร้างชีต('ห้องพัก_Rooms', [
    'Room_ID','ประเภทห้อง','ราคา/วัน','ราคา/เดือน','สถานะ','ผู้เช่าปัจจุบัน','วันเข้าพัก'
  ]);
  
  สร้างชีต('พนักงาน_Staff', [
    'Staff_ID','ชื่อ','ตำแหน่ง','เงินเดือน','เบอร์โทร','วันเริ่มงาน','สถานะ'
  ]);

  // 2. การเงิน (Finance)
  สร้างชีต('รายรับ_Income', [
    'วันที่','ประเภท','Room_ID','Customer_ID','รายการ','จำนวนเงิน','วิธีชำระ','สถานะ'
  ]);
  
  สร้างชีต('รายจ่าย_Expense', [
    'วันที่','หมวดรายจ่าย','รายละเอียด','จำนวนเงิน','ผู้อนุมัติ','ใบเสร็จ','สถานะ'
  ]);
  
  สร้างชีต('ค่าสาธารณูปโภค_Utilities', [
    'เดือน/ปี','Room_ID','ไฟเก่า','ไฟใหม่','น้ำเก่า','น้ำใหม่','ค่าไฟ','ค่าน้ำ','ยอดรวม','สถานะ'
  ]);

  // 3. การจอง (Booking)
  สร้างชีต('การจอง_Bookings', [
    'Booking_ID','Customer_ID','Room_ID','วันเช็คอิน','วันเช็คเอาท์','ราคารวม','สถานะ','หมายเหตุ'
  ]);

  // 4. เอกสาร (Documents)
  สร้างชีต('ใบเสร็จ_Receipts', [
    'Receipt_ID','วันที่','Customer_ID','รายการ','จำนวนเงิน','ยอดรวม','ไฟล์PDF'
  ]);
  
  สร้างชีต('สัญญาเช่า_Contracts', [
    'Contract_ID','Customer_ID','Room_ID','วันเริ่ม','วันสิ้นสุด','ค่าเช่า','เงินประกัน','สถานะ'
  ]);

  // 5. รายงาน (Reports)
  สร้างชีต('รายงานรายเดือน_Monthly', [
    'เดือน/ปี','รายรับรวม','รายจ่ายรวม','กำไร','อัตราเข้าพัก','หมายเหตุ'
  ]);

  // 6. ระบบ (System)
  const ควบคุม = สร้างชีต('ระบบควบคุม_Control', [
    'ชื่อชีต','จำนวนข้อมูล','อัพเดทล่าสุด','สถานะ'
  ]);

  // เพิ่มข้อมูลควบคุม
  const ชีตทั้งหมด = ss.getSheets();
  ชีตทั้งหมด.forEach(sheet => {
    if (sheet.getName() !== 'ระบบควบคุม_Control' && sheet.getName() !== 'Sheet1') {
      ควบคุม.appendRow([sheet.getName(), 0, new Date(), 'Active']);
    }
  });

  // ลบชีตเริ่มต้น
  ss.deleteSheet(ss.getSheetByName('Sheet1'));
  
  return ss.getUrl();
}

function สร้างIDอัตโนมัติ(ประเภท) {
  const วันนี้ = new Date();
  const ปี = วันนี้.getFullYear().toString().slice(-2);
  const เดือน = (วันนี้.getMonth() + 1).toString().padStart(2, '0');
  const วัน = วันนี้.getDate().toString().padStart(2, '0');
  
  const รูปแบบID = {
    'customer': `CUS${ปี}${เดือน}${วัน}`,
    'room': `RM${ปี}${เดือน}${วัน}`,
    'booking': `BK${ปี}${เดือน}${วัน}`,
    'receipt': `RC${ปี}${เดือน}${วัน}`,
    'contract': `CT${ปี}${เดือน}${วัน}`
  };
  
  const baseID = รูปแบบID[ประเภท] || `GEN${ปี}${เดือน}${วัน}`;
  const เลขลำดับ = Math.floor(Math.random() * 900) + 100;
  
  return `${baseID}${เลขลำดับ}`;
}

function คำนวณค่าไฟน้ำ(ไฟเก่า, ไฟใหม่, น้ำเก่า, น้ำใหม่) {
  const หน่วยไฟ = ไฟใหม่ - ไฟเก่า;
  const หน่วยน้ำ = น้ำใหม่ - น้ำเก่า;
  
  // คำนวณค่าไฟแบบขั้นบันได
  let ค่าไฟ = 0;
  if (หน่วยไฟ <= 150) ค่าไฟ = หน่วยไฟ * 3.27;
  else if (หน่วยไฟ <= 400) ค่าไฟ = 150 * 3.27 + (หน่วยไฟ - 150) * 4.22;
  else ค่าไฟ = 150 * 3.27 + 250 * 4.22 + (หน่วยไฟ - 400) * 4.42;
  
  // คำนวณค่าน้ำแบบขั้นบันได
  let ค่าน้ำ = 0;
  if (หน่วยน้ำ <= 8) ค่าน้ำ = หน่วยน้ำ * 8.50;
  else if (หน่วยน้ำ <= 20) ค่าน้ำ = 8 * 8.50 + (หน่วยน้ำ - 8) * 9.50;
  else if (หน่วยน้ำ <= 30) ค่าน้ำ = 8 * 8.50 + 12 * 9.50 + (หน่วยน้ำ - 20) * 10.50;
  else ค่าน้ำ = 8 * 8.50 + 12 * 9.50 + 10 * 10.50 + (หน่วยน้ำ - 30) * 11.50;
  
  return {
    หน่วยไฟ: หน่วยไฟ,
    หน่วยน้ำ: หน่วยน้ำ,
    ค่าไฟ: Math.round(ค่าไฟ * 100) / 100,
    ค่าน้ำ: Math.round(ค่าน้ำ * 100) / 100,
    ยอดรวม: Math.round((ค่าไฟ + ค่าน้ำ) * 100) / 100
  };
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;
    
    switch (action) {
      case 'create_system':
        const url = สร้างระบบโรงแรมแบบกระชับ();
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          message: 'สร้างระบบเรียบร้อย',
          url: url
        })).setMimeType(ContentService.MimeType.JSON);
        
      case 'generate_id':
        const id = สร้างIDอัตโนมัติ(data.type);
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          id: id
        })).setMimeType(ContentService.MimeType.JSON);
        
      case 'calculate_utilities':
        const result = คำนวณค่าไฟน้ำ(data.ไฟเก่า, data.ไฟใหม่, data.น้ำเก่า, data.น้ำใหม่);
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          data: result
        })).setMimeType(ContentService.MimeType.JSON);
        
      case 'add_data':
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const sheet = ss.getSheetByName(data.sheet);
        if (sheet) {
          sheet.appendRow(Object.values(data.data));
          return ContentService.createTextOutput(JSON.stringify({
            success: true,
            message: 'เพิ่มข้อมูลสำเร็จ'
          })).setMimeType(ContentService.MimeType.JSON);
        }
        break;
        
      default:
        return ContentService.createTextOutput(JSON.stringify({
          success: false,
          message: 'ไม่รู้จักคำสั่งนี้'
        })).setMimeType(ContentService.MimeType.JSON);
    }
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
