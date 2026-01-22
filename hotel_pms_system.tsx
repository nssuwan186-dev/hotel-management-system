import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, BedDouble, Users, DollarSign, Calendar, ClipboardList, 
  LogOut, Plus, CheckCircle, AlertCircle, Clock, X, Save, Edit, Trash2,
  Home, FileText, Settings, Search, Filter, ChevronLeft, ChevronRight, Menu
} from 'lucide-react';

// ============================================================================
// INITIAL DATA (ข้อมูลเริ่มต้น - Data Tier)
// ============================================================================

const INITIAL_ROOMS = [
  { id: 'RID-00101', name: '101', type: 'Deluxe', status: 'Occupied', price: 2500, tenant: 'สมชาย ใจดี' },
  { id: 'RID-00102', name: '102', type: 'Deluxe', status: 'Available', price: 2500, tenant: '-' },
  { id: 'RID-00201', name: '201', type: 'Suite', status: 'Maintenance', price: 4500, tenant: '-' },
  { id: 'RID-00202', name: '202', type: 'Suite', status: 'Available', price: 4500, tenant: '-' },
];

const INITIAL_CUSTOMERS = [
  { id: 'CUS-00001', name: 'สมชาย ใจดี', phone: '081-234-5678', email: 'somchai@email.com' },
  { id: 'CUS-00002', name: 'สมหญิง รักษ์ดี', phone: '082-345-6789', email: 'somying@email.com' },
];

const INITIAL_BOOKINGS = [
  {
    id: 'RES-00001',
    customerId: 'CUS-00001',
    roomId: 'RID-00101',
    checkIn: '2026-01-25',
    checkOut: '2026-01-27',
    status: 'Checked-in',
    dailyRate: 2500,
    totalAmount: 5000,
  },
];

const INITIAL_TRANSACTIONS = [
  { 
    id: 'TXN-20260122-001', 
    date: '2026-01-22', 
    category: 'รายได้ค่าห้อง', 
    type: 'income', 
    amount: 15000, 
    detail: 'สรุปยอดรายวัน',
    bookingId: 'RES-00001'
  },
  { 
    id: 'TXN-20260122-002', 
    date: '2026-01-22', 
    category: 'ค่าน้ำ-ค่าไฟ', 
    type: 'expense', 
    amount: 4500, 
    detail: 'ชำระการไฟฟ้า',
    bookingId: null
  },
];

const INITIAL_STAFF = [
  { id: 'EMP001', name: 'สมศรี ขยันงาน', position: 'แม่บ้าน', salary: 12000, status: 'Active' },
  { id: 'EMP002', name: 'บุญมี รักษา', position: 'รปภ.', salary: 13000, status: 'Active' },
];

const INITIAL_TASKS = [
  { id: 1, task: 'จ่ายค่าขยะเทศบาล', dueDate: '2026-02-05', status: 'Pending', type: 'Recurring' },
  { id: 2, task: 'ส่งภาษีประจำเดือน', dueDate: '2026-02-10', status: 'Pending', type: 'Recurring' },
  { id: 3, task: 'ตรวจเช็คแอร์ประจำปี ตึก A', dueDate: '2026-02-15', status: 'In Progress', type: 'Maintenance' },
];

// ============================================================================
// UTILITY COMPONENTS
// ============================================================================

const Card = ({ title, value, subtext, icon: Icon, colorClass }) => (
  <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between hover:shadow-md transition-shadow">
    <div>
      <p className="text-slate-500 text-sm font-medium mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-slate-800">{value}</h3>
      {subtext && <p className={`text-xs mt-2 ${colorClass}`}>{subtext}</p>}
    </div>
    <div className={`p-3 rounded-lg ${colorClass.replace('text-', 'bg-').replace('600', '100')}`}>
      <Icon className={`w-6 h-6 ${colorClass}`} />
    </div>
  </div>
);

const StatusBadge = ({ status }) => {
  const styles = {
    Available: 'bg-green-100 text-green-700',
    Occupied: 'bg-red-100 text-red-700',
    Maintenance: 'bg-gray-100 text-gray-700',
    Confirmed: 'bg-blue-100 text-blue-800',
    'Checked-in': 'bg-green-100 text-green-800',
    'Checked-out': 'bg-gray-100 text-gray-600',
    Cancelled: 'bg-red-100 text-red-600',
    Active: 'bg-green-100 text-green-700',
    Pending: 'bg-yellow-100 text-yellow-700',
    'In Progress': 'bg-blue-100 text-blue-700',
    Completed: 'bg-green-100 text-green-700',
  };
  
  const label = {
    Available: 'ว่าง',
    Occupied: 'ไม่ว่าง',
    Maintenance: 'ซ่อมแซม',
    Confirmed: 'ยืนยันแล้ว',
    'Checked-in': 'เข้าพักแล้ว',
    'Checked-out': 'เช็คเอาท์',
    Cancelled: 'ยกเลิก',
    Active: 'ปกติ',
    Pending: 'รอดำเนินการ',
    'In Progress': 'กำลังทำ',
    Completed: 'เสร็จสิ้น',
  };
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100'}`}>
      {label[status] || status}
    </span>
  );
};

const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b flex justify-between items-center bg-slate-50">
          <h3 className="font-bold text-lg text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-red-500 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="p-6 max-h-96 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function HotelPMS() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  const [rooms, setRooms] = useState(INITIAL_ROOMS);
  const [customers, setCustomers] = useState(INITIAL_CUSTOMERS);
  const [bookings, setBookings] = useState(INITIAL_BOOKINGS);
  const [transactions, setTransactions] = useState(INITIAL_TRANSACTIONS);
  const [staff, setStaff] = useState(INITIAL_STAFF);
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [conflicts, setConflicts] = useState([]);

  const [modalType, setModalType] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    detectConflicts(bookings);
  }, [bookings]);

  const detectConflicts = (bookingList) => {
    const occupancyMap = new Map();
    const detectedConflicts = [];

    bookingList.forEach(booking => {
      if (booking.status === 'Cancelled') return;
      
      const start = new Date(booking.checkIn);
      const end = new Date(booking.checkOut);
      
      for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
        const dateStr = d.toISOString().split('T')[0];
        const key = `${dateStr}_${booking.roomId}`;
        
        if (occupancyMap.has(key)) {
          detectedConflicts.push({
            date: dateStr,
            roomId: booking.roomId,
            bookings: [occupancyMap.get(key), booking.id]
          });
        } else {
          occupancyMap.set(key, booking.id);
        }
      }
    });

    setConflicts(detectedConflicts);
  };

  const generateId = (prefix, list, dateBasedId = false) => {
    if (dateBasedId) {
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      const todayTransactions = list.filter(t => t.id && t.id.includes(date));
      const seq = String(todayTransactions.length + 1).padStart(3, '0');
      return `${prefix}-${date}-${seq}`;
    }
    
    const maxId = list.reduce((max, item) => {
      const numPart = item.id.split('-')[1];
      const num = parseInt(numPart);
      return num > max ? num : max;
    }, 0);
    return `${prefix}-${String(maxId + 1).padStart(5, '0')}`;
  };

  const generateAccountingEntry = (booking) => {
    const txnId = generateId('TXN', transactions, true);
    
    const entry = {
      id: txnId,
      bookingId: booking.id,
      date: new Date().toISOString().split('T')[0],
      category: 'รายได้ค่าห้อง',
      type: 'income',
      amount: booking.totalAmount,
      detail: `เงินมัดจำ - ${booking.id}`,
    };
    
    setTransactions([entry, ...transactions]);
  };

  const handleOpenModal = (type, data = {}) => {
    setModalType(type);
    setFormData(data);
  };

  const handleCloseModal = () => {
    setModalType(null);
    setFormData({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    if (modalType === 'addRoom') {
      const newRoom = {
        id: formData.id || generateId('RID', rooms),
        name: formData.name || formData.id,
        type: formData.type || 'Deluxe',
        status: formData.status || 'Available',
        price: Number(formData.price) || 2500,
        tenant: formData.tenant || '-'
      };
      setRooms([...rooms, newRoom]);
    } else if (modalType === 'editRoom') {
      setRooms(rooms.map(room => 
        room.id === formData.id ? { ...room, ...formData, price: Number(formData.price) } : room
      ));
    } else if (modalType === 'addBooking') {
      if (!formData.customerId || !formData.roomId || !formData.checkIn || !formData.checkOut) {
        alert('กรุณากรอกข้อมูลให้ครบถ้วน');
        return;
      }
      const nights = Math.ceil((new Date(formData.checkOut) - new Date(formData.checkIn)) / (1000 * 60 * 60 * 24));
      const newBooking = {
        id: generateId('RES', bookings),
        customerId: formData.customerId,
        roomId: formData.roomId,
        checkIn: formData.checkIn,
        checkOut: formData.checkOut,
        status: 'Confirmed',
        dailyRate: Number(formData.dailyRate) || 2500,
        totalAmount: Number(formData.dailyRate || 2500) * nights
      };
      setBookings([...bookings, newBooking]);
      generateAccountingEntry(newBooking);
    } else if (modalType === 'editBooking') {
      setBookings(bookings.map(b => 
        b.id === formData.id ? { ...formData } : b
      ));
    } else if (modalType === 'addTxn') {
      const newTxn = {
        id: generateId('TXN', transactions, true),
        date: formData.date || new Date().toISOString().split('T')[0],
        category: formData.category || 'อื่นๆ',
        type: formData.type || 'expense',
        amount: Number(formData.amount) || 0,
        detail: formData.detail || '-',
        bookingId: null
      };
      setTransactions([newTxn, ...transactions]);
    } else if (modalType === 'editTxn') {
      setTransactions(transactions.map(txn => 
        txn.id === formData.id ? { ...txn, ...formData, amount: Number(formData.amount) } : txn
      ));
    } else if (modalType === 'addStaff') {
      const newStaff = {
        id: `EMP${Math.floor(Math.random() * 1000)}`,
        name: formData.name,
        position: formData.position,
        salary: Number(formData.salary),
        status: 'Active'
      };
      setStaff([...staff, newStaff]);
    } else if (modalType === 'editStaff') {
      setStaff(staff.map(person => 
        person.id === formData.id ? { ...person, ...formData, salary: Number(formData.salary) } : person
      ));
    } else if (modalType === 'addTask') {
      const newTask = {
        id: tasks.length + 1,
        task: formData.task,
        dueDate: formData.dueDate || new Date().toISOString().split('T')[0],
        status: 'Pending',
        type: formData.type || 'Recurring'
      };
      setTasks([...tasks, newTask]);
    } else if (modalType === 'editTask') {
      setTasks(tasks.map(task => 
        task.id === formData.id ? { ...task, ...formData } : task
      ));
    }

    handleCloseModal();
  };

  const totalRooms = rooms.length;
  const occupiedRooms = rooms.filter(r => r.status === 'Occupied').length;
  const occupancyRate = totalRooms > 0 ? ((occupiedRooms / totalRooms) * 100).toFixed(1) : 0;
  
  const totalIncome = transactions.filter(t => t.type === 'income').reduce((acc, curr) => acc + Number(curr.amount), 0);
  const totalExpense = transactions.filter(t => t.type === 'expense').reduce((acc, curr) => acc + Number(curr.amount), 0);
  const netProfit = totalIncome - totalExpense;

  const menuItems = [
    { id: 'dashboard', label: 'ภาพรวม', icon: LayoutDashboard },
    { id: 'rooms', label: 'ห้องพัก', icon: BedDouble },
    { id: 'bookings', label: 'การจอง', icon: Calendar },
    { id: 'accounting', label: 'บัญชี', icon: DollarSign },
    { id: 'staff', label: 'พนักงาน', icon: Users },
    { id: 'planning', label: 'วางแผนงาน', icon: ClipboardList },
  ];

  const renderContent = () => {
    if (activeTab === 'dashboard') {
      return (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-800">ภาพรวมกิจการ</h2>
          
          {conflicts.length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-center">
                <AlertCircle className="w-6 h-6 text-red-500 mr-3" />
                <div>
                  <h3 className="text-red-800 font-bold">⚠️ พบการจองห้องซ้ำซ้อน!</h3>
                  <p className="text-red-700 text-sm mt-1">พบข้อขัดแย้ง {conflicts.length} รายการ</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card title="อัตราการเข้าพัก" value={`${occupancyRate}%`} subtext={`${occupiedRooms} จาก ${totalRooms} ห้อง`} icon={BedDouble} colorClass="text-blue-600" />
            <Card title="รายได้ทั้งหมด" value={`฿${totalIncome.toLocaleString()}`} subtext="รวมทุกประเภท" icon={DollarSign} colorClass="text-green-600" />
            <Card title="ค่าใช้จ่ายรวม" value={`฿${totalExpense.toLocaleString()}`} subtext="สาธารณูปโภคและค่าจ้าง" icon={ClipboardList} colorClass="text-red-600" />
            <Card title="กำไรสุทธิ" value={`฿${netProfit.toLocaleString()}`} subtext="รายรับ - รายจ่าย" icon={CheckCircle} colorClass="text-purple-600" />
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="font-bold text-lg mb-4 text-slate-700">สถานะห้องพักวันนี้</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {rooms.map(room => (
                <div key={room.id} onClick={() => handleOpenModal('editRoom', room)}
                  className={`p-4 rounded-lg border flex flex-col items-center justify-center text-center transition-all cursor-pointer hover:scale-105 shadow-sm hover:shadow-md ${
                    room.status === 'Available' ? 'bg-green-50 border-green-200' : 
                    room.status === 'Occupied' ? 'bg-red-50 border-red-200' : 'bg-gray-100 border-gray-200'
                  }`}>
                  <span className="font-bold text-slate-700">{room.name}</span>
                  <span className="text-xs text-slate-500 mb-1">{room.type}</span>
                  <StatusBadge status={room.status} />
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (activeTab === 'rooms') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">จัดการห้องพัก</h2>
            <button onClick={() => handleOpenModal('addRoom')} className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
              <Plus size={18} /> เพิ่มห้องพัก
            </button>
          </div>
          <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-50 text-slate-600 border-b">
                <tr>
                  <th className="p-4">เลขห้อง</th>
                  <th className="p-4">ประเภท</th>
                  <th className="p-4">ราคา/คืน</th>
                  <th className="p-4">ผู้เข้าพัก</th>
                  <th className="p-4">สถานะ</th>
                  <th className="p-4">จัดการ</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {rooms.map(room => (
                  <tr key={room.id} className="hover:bg-slate-50">
                    <td className="p-4 font-medium">{room.name}</td>
                    <td className="p-4">{room.type}</td>
                    <td className="p-4">฿{room.price.toLocaleString()}</td>
                    <td className="p-4 text-slate-600">{room.tenant}</td>
                    <td className="p-4"><StatusBadge status={room.status} /></td>
                    <td className="p-4">
                      <button onClick={() => handleOpenModal('editRoom', room)} className="flex items-center gap-1 text-blue-600 hover:text-blue-800">
                        <Edit size={16} /> แก้ไข
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    if (activeTab === 'bookings') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">จัดการการจอง</h2>
            <button onClick={() => handleOpenModal('addBooking')} className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
              <Plus size={18} /> เพิ่มการจอง
            </button>
          </div>
          <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">Booking ID</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">ลูกค้า</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">ห้อง</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">Check-in</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">Check-out</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">ยอดรวม</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">สถานะ</th>
                  <th className="p-4 text-left text-xs font-medium text-slate-500 uppercase">จัดการ</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {bookings.map(booking => {
                  const customer = customers.find(c => c.id === booking.customerId);
                  const room = rooms.find(r => r.id === booking.roomId);
                  return (
                    <tr key={booking.id} className="hover:bg-slate-50">
                      <td className="p-4 font-mono text-sm">{booking.id}</td>
                      <td className="p-4">{customer?.name}</td>
                      <td className="p-4">{room?.name}</td>
                      <td className="p-4 text-sm">{booking.checkIn}</td>
                      <td className="p-4 text-sm">{booking.checkOut}</td>
                      <td className="p-4 font-semibold">฿{booking.totalAmount.toLocaleString()}</td>
                      <td className="p-4"><StatusBadge status={booking.status} /></td>
                      <td className="p-4">
                        <button onClick={() => handleOpenModal('editBooking', booking)} className="text-blue-600 hover:text-blue-800">
                          <Edit size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    if (activeTab === 'accounting') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">บัญชีรายรับ-รายจ่าย</h2>
            <button onClick={() => handleOpenModal('addTxn')} className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700">
              <Plus size={18} /> บันทึกรายการ
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm text-gray-600 mb-2">รายรับทั้งหมด</h3>
              <p className="text-3xl font-bold text-green-600">฿{totalIncome.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm text-gray-600 mb-2">รายจ่ายทั้งหมด</h3>
              <p className="text-3xl font-bold text-red-600">฿{totalExpense.toLocaleString()}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-50 text-slate-600 border-b">
                <tr>
                  <th className="p-4">Transaction ID</th>
                  <th className="p-4">วันที่</th>
                  <th className="p-4">หมวดหมู่</th>
                  <th className="p-4">รายละเอียด</th>
                  <th className="p-4">ประเภท</th>
                  <th className="p-4 text-right">จำนวนเงิน</th>
                  <th className="p-4">จัดการ</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {transactions.map(txn => (
                  <tr key={txn.id} className="hover:bg-slate-50">
                    <td className="p-4 font-mono text-xs">{txn.id}</td>
                    <td className="p-4">{txn.date}</td>
                    <td className="p-4"><span className="px-2 py-1 bg-slate-100 rounded text-xs">{txn.category}</span></td>
                    <td className="p-4 text-slate-600">{txn.detail}</td>
                    <td className={`p-4 font-medium ${txn.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                      {txn.type === 'income' ? 'รายรับ' : 'รายจ่าย'}
                    </td>
                    <td className="p-4 text-right font-medium">฿{Number(txn.amount).toLocaleString()}</td>
                    <td className="p-4">
                      <button onClick={() => handleOpenModal('editTxn', txn)} className="text-blue-600 hover:text-blue-800">
                        <Edit size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    if (activeTab === 'staff') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">บุคคลและเงินเดือน</h2>
            <button onClick={() => handleOpenModal('addStaff')} className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700">
              <Plus size={18} /> เพิ่มพนักงาน
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {staff.map(person => (
              <div key={person.id} className="bg-white p-5 rounded-xl border shadow-sm flex items-center gap-4 relative">
                <button onClick={() => handleOpenModal('editStaff', person)} className="absolute top-3 right-3 text-slate-400 hover:text-blue-600">
                  <Edit size={16} />
                </button>
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold">
                  {person.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-bold text-slate-800">{person.name}</h4>
                  <p className="text-sm text-slate-500">{person.position}</p>
                  <p className="text-xs text-slate-400 mt-1">เงินเดือน: ฿{person.salary.toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (activeTab === 'planning') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">วางแผนและงานประจำเดือน</h2>
            <button onClick={() => handleOpenModal('addTask')} className="bg-orange-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-orange-700">
              <Plus size={18} /> เพิ่มงานใหม่
            </button>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="space-y-4">
              {tasks.map(task => (
                <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-full ${task.type === 'Recurring' ? 'bg-orange-100 text-orange-600' : 'bg-blue-100 text-blue-600'}`}>
                      {task.type === 'Recurring' ? <Clock size={20}/> : <ClipboardList size={20}/>}
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-700">{task.task}</h4>
                      <p className="text-sm text-slate-500">กำหนดส่ง: {task.dueDate}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <StatusBadge status={task.status} />
                    <button onClick={() => handleOpenModal('editTask', task)} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full">
                      <Edit size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return <div>เลือกเมนู</div>;
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      <aside className={`bg-slate-900 text-slate-300 flex flex-col shrink-0 transition-all duration-300 ${sidebarCollapsed ? 'w-20' : 'w-64'}`}>
        <div className={`p-4 border-b border-slate-700 flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'}`}>
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-xl font-bold text-white">🏨 HOTEL PMS</h1>
              <p className="text-xs text-slate-400 mt-1">3-Tier System</p>
            </div>
          )}
          <button 
            onClick={() => setSidebarCollapsed(prev => !prev)} 
            className="p-2 hover:bg-slate-800 rounded-lg transition flex items-center justify-center"
          >
            {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>
        
        <nav className="flex-1 p-2 space-y-2 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button 
                key={item.id} 
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center' : 'gap-3'} px-3 py-3 rounded-lg transition-all ${
                  activeTab === item.id ? 'bg-blue-600 text-white shadow-md' : 'hover:bg-slate-800 hover:text-white'
                }`}
                title={item.label}
              >
                <Icon size={20} className="flex-shrink-0" />
                {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {!sidebarCollapsed && (
          <div className="p-3 border-t border-slate-700">
            <div className="bg-slate-800 rounded-lg p-2 text-xs">
              <p className="text-slate-400 text-xs">Architecture</p>
              <p className="text-white font-semibold text-xs">Data → Workflow → UI</p>
              <p className="text-slate-400 mt-1 text-xs">PARA + CODE</p>
            </div>
          </div>
        )}
      </aside>

      <main className="flex-1 overflow-y-auto">
        <header className="bg-white shadow-sm px-8 py-4 flex justify-between items-center sticky top-0 z-10">
          <h2 className="font-semibold text-slate-700">
            {menuItems.find(m => m.id === activeTab)?.label || 'Dashboard'}
          </h2>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-sm font-bold text-slate-700">Admin User</p>
              <p className="text-xs text-slate-500">ผู้จัดการทั่วไป</p>
            </div>
            <div className="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center">
              <Users size={20} className="text-slate-600" />
            </div>
          </div>
        </header>

        <div className="p-8">
          {renderContent()}
        </div>
      </main>

      <Modal isOpen={modalType === 'addRoom' || modalType === 'editRoom'} onClose={handleCloseModal} title={modalType === 'addRoom' ? "เพิ่มห้องพักใหม่" : "แก้ไขข้อมูลห้องพัก"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">เลขห้อง</label>
            <input name="name" value={formData.name || ''} onChange={handleInputChange} placeholder="เช่น 101" className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ประเภทห้อง</label>
            <select name="type" value={formData.type || 'Deluxe'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="Deluxe">Deluxe</option>
              <option value="Suite">Suite</option>
              <option value="Standard">Standard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ราคาต่อคืน</label>
            <input name="price" type="number" value={formData.price || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">สถานะห้อง</label>
            <select name="status" value={formData.status || 'Available'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="Available">ว่าง</option>
              <option value="Occupied">มีผู้เข้าพัก</option>
              <option value="Maintenance">ปิดซ่อมแซม</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ชื่อผู้เข้าพัก</label>
            <input name="tenant" value={formData.tenant || ''} onChange={handleInputChange} placeholder="ใส่ชื่อลูกค้า" className="w-full p-2 border rounded-lg" />
          </div>
          <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex justify-center items-center gap-2">
            <Save size={18} /> บันทึกข้อมูล
          </button>
        </div>
      </Modal>

      <Modal isOpen={modalType === 'addBooking' || modalType === 'editBooking'} onClose={handleCloseModal} title={modalType === 'addBooking' ? "สร้างการจองใหม่" : "แก้ไขการจอง"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ลูกค้า</label>
            <select name="customerId" value={formData.customerId || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="">เลือกลูกค้า</option>
              {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ห้องพัก</label>
            <select name="roomId" value={formData.roomId || ''} onChange={(e) => {
              const room = rooms.find(r => r.id === e.target.value);
              setFormData({...formData, roomId: e.target.value, dailyRate: room?.price || 0});
            }} className="w-full p-2 border rounded-lg">
              <option value="">เลือกห้อง</option>
              {rooms.map(r => <option key={r.id} value={r.id}>{r.name} - {r.type} ({r.price} บาท/คืน)</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Check-in</label>
            <input type="date" name="checkIn" value={formData.checkIn || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Check-out</label>
            <input type="date" name="checkOut" value={formData.checkOut || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          {modalType === 'editBooking' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">สถานะ</label>
              <select name="status" value={formData.status || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
                <option value="Confirmed">ยืนยันแล้ว</option>
                <option value="Checked-in">เข้าพักแล้ว</option>
                <option value="Checked-out">เช็คเอาท์</option>
                <option value="Cancelled">ยกเลิก</option>
              </select>
            </div>
          )}
          <button onClick={handleSubmit} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex justify-center items-center gap-2">
            <Save size={18} /> บันทึกการจอง
          </button>
        </div>
      </Modal>

      <Modal isOpen={modalType === 'addTxn' || modalType === 'editTxn'} onClose={handleCloseModal} title={modalType === 'addTxn' ? "บันทึกรายการบัญชี" : "แก้ไขรายการ"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ประเภทรายการ</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="type" value="income" checked={formData.type === 'income' || !formData.type} onChange={handleInputChange} />
                <span className="text-green-600 font-medium">รายรับ</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="type" value="expense" checked={formData.type === 'expense'} onChange={handleInputChange} />
                <span className="text-red-600 font-medium">รายจ่าย</span>
              </label>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">วันที่</label>
            <input name="date" type="date" value={formData.date || new Date().toISOString().split('T')[0]} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">จำนวนเงิน</label>
            <input name="amount" type="number" value={formData.amount || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">รายละเอียด</label>
            <input name="detail" value={formData.detail || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">หมวดหมู่</label>
            <select name="category" value={formData.category || 'อื่นๆ'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="รายได้ค่าห้อง">รายได้ค่าห้อง</option>
              <option value="ค่าน้ำ-ค่าไฟ">ค่าน้ำ-ค่าไฟ</option>
              <option value="ค่าจ้างพนักงาน">ค่าจ้างพนักงาน</option>
              <option value="ค่าซ่อมแซม">ค่าซ่อมแซม</option>
              <option value="อื่นๆ">อื่นๆ</option>
            </select>
          </div>
          <button onClick={handleSubmit} className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 flex justify-center items-center gap-2">
            <Save size={18} /> บันทึกรายการ
          </button>
        </div>
      </Modal>

      <Modal isOpen={modalType === 'addStaff' || modalType === 'editStaff'} onClose={handleCloseModal} title={modalType === 'addStaff' ? "เพิ่มพนักงานใหม่" : "แก้ไขข้อมูลพนักงาน"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ชื่อ-นามสกุล</label>
            <input name="name" value={formData.name || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ตำแหน่ง</label>
            <select name="position" value={formData.position || 'แม่บ้าน'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="แม่บ้าน">แม่บ้าน</option>
              <option value="รปภ.">รปภ.</option>
              <option value="บัญชี">บัญชี</option>
              <option value="ผู้จัดการ">ผู้จัดการ</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">เงินเดือน</label>
            <input name="salary" type="number" value={formData.salary || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <button onClick={handleSubmit} className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 flex justify-center items-center gap-2">
            <Save size={18} /> บันทึกข้อมูล
          </button>
        </div>
      </Modal>

      <Modal isOpen={modalType === 'addTask' || modalType === 'editTask'} onClose={handleCloseModal} title={modalType === 'addTask' ? "เพิ่มงานใหม่" : "แก้ไขงาน"}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ชื่องาน</label>
            <input name="task" value={formData.task || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">วันกำหนดส่ง</label>
            <input name="dueDate" type="date" value={formData.dueDate || ''} onChange={handleInputChange} className="w-full p-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">ประเภทงาน</label>
            <select name="type" value={formData.type || 'Recurring'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
              <option value="Recurring">งานประจำ</option>
              <option value="Maintenance">ซ่อมบำรุง</option>
              <option value="General">ทั่วไป</option>
            </select>
          </div>
          {modalType === 'editTask' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">สถานะ</label>
              <select name="status" value={formData.status || 'Pending'} onChange={handleInputChange} className="w-full p-2 border rounded-lg">
                <option value="Pending">รอดำเนินการ</option>
                <option value="In Progress">กำลังทำ</option>
                <option value="Completed">เสร็จสิ้น</option>
              </select>
            </div>
          )}
          <button onClick={handleSubmit} className="w-full bg-orange-600 text-white py-2 rounded-lg hover:bg-orange-700 flex justify-center items-center gap-2">
            <Save size={18} /> บันทึกงาน
          </button>
        </div>
      </Modal>

    </div>
  );
}
          