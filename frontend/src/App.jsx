// App.jsx - Responsive Hotel Billing with boxed menu cards + qty controls
import React, { useState, useContext, createContext, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
  useNavigate,
  useParams
} from "react-router-dom";
import './styles.css';

/* -------------------- App State Context -------------------- */
const AppContext = createContext(null);
export function useApp() { return useContext(AppContext); }

function generateId(prefix = "B") {
  return `${prefix}${Date.now().toString().slice(-6)}`;
}

const LS_KEYS = { menu: 'hb:menu', tables: 'hb:tables', waiters: 'hb:waiters', users: 'hb:users', bills: 'hb:bills' };

/* -------------------- Mock initial data -------------------- */
const initialMenu = [
  { id: 'm1', name: 'Margherita Pizza', price: 250, gst: 0.05 },
  { id: 'm2', name: 'Veg Biryani', price: 180, gst: 0.12 },
  { id: 'm3', name: 'Cold Coffee', price: 90, gst: 0.05 },
  { id: 'm4', name: 'Paneer Butter Masala', price: 220, gst: 0.05 },
  { id: 'm5', name: 'Tandoori Chicken', price: 320, gst: 0.05 }
];
const initialTables = Array.from({length:8}).map((_,i)=>({ id:`T${i+1}`, name:`Table ${i+1}`, currentBillId: null }));
const initialWaiters = [{id: 'w1', name: 'Ravi'}, {id:'w2', name:'Suma'}, {id:'w3', name:'Priya'}];
const initialUsers = [
  { id: 'admin', name: 'Administrator', role: 'admin', password: 'admin123' },
  { id: 'ravi', name: 'Ravi', role: 'staff', password: 'ravi123' },
  { id: 'suma', name: 'Suma', role: 'staff', password: 'suma123' }
];

/* -------------------- Provider -------------------- */
function safeLoad(key, fallback){
  try{ const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback }catch(e){ return fallback }
}

function AppProvider({children}){
  const [menu, setMenu] = useState(()=> safeLoad(LS_KEYS.menu, initialMenu));
  const [tables, setTables] = useState(()=> safeLoad(LS_KEYS.tables, initialTables));
  const [waiters, setWaiters] = useState(()=> safeLoad(LS_KEYS.waiters, initialWaiters));
  const [bills, setBills] = useState(()=> safeLoad(LS_KEYS.bills, []));
  const [users, setUsers] = useState(()=> safeLoad(LS_KEYS.users, initialUsers));
  const [user, setUser] = useState(null);

  useEffect(()=> localStorage.setItem(LS_KEYS.menu, JSON.stringify(menu)), [menu]);
  useEffect(()=> localStorage.setItem(LS_KEYS.tables, JSON.stringify(tables)), [tables]);
  useEffect(()=> localStorage.setItem(LS_KEYS.waiters, JSON.stringify(waiters)), [waiters]);
  useEffect(()=> localStorage.setItem(LS_KEYS.bills, JSON.stringify(bills)), [bills]);
  useEffect(()=> localStorage.setItem(LS_KEYS.users, JSON.stringify(users)), [users]);

  const addMenuItem = (item) => setMenu(m=>[...m, item]);
  const updateMenuItem = (id, patch) => setMenu(m=>m.map(it=> it.id===id ? {...it, ...patch} : it));
  const deleteMenuItem = (id) => setMenu(m=>m.filter(it=>it.id!==id));
  const addTable = (tableName) => {
    const id = `T${tables.length+1}`;
    setTables(t=>[...t, {id, name: tableName, currentBillId: null}]);
  }
  const addWaiter = (name) => setWaiters(w=>[...w, {id: `w${Date.now()}`, name}]);
  const addUser = ({id, name, role, password})=>{
    if(users.find(u=>u.id === id)) return { ok:false, msg:'User id already exists' };
    setUsers(u=>[...u, { id, name, role, password }]);
    return { ok:true };
  }

  const createBill = ({tableId, waiterName}) => {
    const id = generateId('B');
    const newBill = { id, tableId, waiterName, items: [], createdAt: new Date().toISOString(), paid: false };
    setBills(b=>[newBill, ...b]);
    setTables(t=>t.map(x=> x.id===tableId ? {...x, currentBillId: id} : x));
    return id;
  }

  const addItemToBill = (billId, menuItem, qty=1) => {
    setBills(b=>b.map(bl=>bl.id===billId ? {...bl, items: addOrUpdateItem(bl.items, menuItem, qty)} : bl));
  }
  function addOrUpdateItem(items, menuItem, qty){
    const idx = items.findIndex(i=>i.id===menuItem.id);
    if(idx>=0){ const copy = [...items]; copy[idx].qty += qty; if(copy[idx].qty<=0) copy.splice(idx,1); return copy; }
    return [...items, { ...menuItem, qty }];
  }

  // NEW: change item qty by delta (positive or negative)
  const changeItemQty = (billId, itemId, delta = 1) => {
    setBills(prevBills => {
      return prevBills.map(bl => {
        if (bl.id !== billId) return bl;
        const items = [...(bl.items || [])];
        const idx = items.findIndex(i => i.id === itemId);
        if (idx === -1) {
          if (delta > 0) {
            const menuItem = menu.find(m => m.id === itemId);
            if (!menuItem) return bl;
            items.push({ ...menuItem, qty: delta });
          }
        } else {
          items[idx].qty = (Number(items[idx].qty) || 0) + delta;
          if (items[idx].qty <= 0) items.splice(idx, 1);
        }
        return { ...bl, items };
      });
    });
  }

  const removeItemFromBill = (billId, itemId) => setBills(b=>b.map(bl=> bl.id===billId ? {...bl, items: bl.items.filter(i=>i.id!==itemId)} : bl));
  const finalizeBill = (billId) => {
    const billObj = bills.find(x=>x.id===billId);
    setBills(b=>b.map(bl=> bl.id===billId ? {...bl, paid:true, finalizedAt: new Date().toISOString()} : bl));
    if(billObj) setTables(t=>t.map(x=> x.id===billObj.tableId ? {...x, currentBillId: null} : x));
  }

  const value = { menu, addMenuItem, updateMenuItem, deleteMenuItem, tables, addTable, waiters, addWaiter, bills, createBill, addItemToBill, changeItemQty, removeItemFromBill, finalizeBill, users, addUser, user, setUser };
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

/* -------------------- Dashboard (Admin only) -------------------- */
function Dashboard(){
  const { menu, bills, tables } = useApp();
  const navigate = useNavigate();

  const totalProducts = (menu || []).length;
  const totalBills = (bills || []).length;
  const totalRevenue = (bills || []).filter(b => b.paid).reduce((sum, b) => {
    const billTotal = (b.items || []).reduce((s, it) => {
      const subtotal = (Number(it.price) || 0) * (Number(it.qty) || 0);
      const gst = subtotal * (Number(it.gst) || 0);
      return s + subtotal + gst;
    }, 0);
    return sum + billTotal;
  }, 0);

  const fmt = (val) => new Intl.NumberFormat('en-IN', { style:'currency', currency:'INR' }).format(val);

  return (
    <div className="dashboard-page">
      <h2 className="h2">Dashboard</h2>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="muted">TOTAL REVENUE</div>
          <div className="dashboard-value">{fmt(totalRevenue)}</div>
        </div>

        <div className="dashboard-card">
          <div className="muted">TOTAL BILLS</div>
          <div className="dashboard-value">{totalBills}</div>
        </div>

        <div className="dashboard-card">
          <div className="muted">TOTAL PRODUCTS</div>
          <div className="dashboard-value">{totalProducts}</div>
        </div>
      </div>

      <div className="card quick-actions-card">
        <div className="h3">Quick Actions</div>
        <div className="quick-actions">
          <button className="btn btn-primary action-btn" onClick={()=>navigate('/tables')}>＋ New Bill</button>
          <button className="btn btn-primary action-btn" onClick={()=>navigate('/menu')}>⚙️ Manage Menu</button>
          <button className="btn btn-primary action-btn" onClick={()=>navigate('/bills')}>🧾 View Bill History</button>
        </div>
      </div>
    </div>
  )
}

/* -------------------- Login Page -------------------- */
function LoginPage(){
  const { setUser, users } = useApp();
  const navigate = useNavigate();
  const [userid, setUserId] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e)=>{
    e.preventDefault();
    if(!userid.trim()) return alert('Enter user id');
    if(!password) return alert('Enter password');
    const matched = users.find(u=>u.id === userid && u.password === password);
    if(!matched) return alert('Invalid credentials');
    setUser({ id: matched.id, name: matched.name, role: matched.role });
    if(matched.role === 'admin') navigate('/dashboard');
    else navigate('/tables');
  }
  return (
    <div className="login-container">
      <form onSubmit={handleLogin} className="card login-card">
        <div className="login-icon">🍽️</div>
        <h2 className="h1">Hotel Billing</h2>
        <p className="muted" style={{marginBottom:20, textAlign:'center'}}>Sign in with your staff/admin account</p>
        <label className="label">User ID</label>
        <input value={userid} onChange={e=>setUserId(e.target.value)} className="input" />
        <label className="label" style={{marginTop:12}}>Password</label>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="input" />
        <button className="btn btn-primary" style={{width:'100%', marginTop:16}}>Sign in</button>
        <div className="demo-info">Demo: admin/admin123, ravi/ravi123, suma/suma123</div>
      </form>
    </div>
  )
}

/* -------------------- Layout & Navbar with Burger Menu -------------------- */
function Layout({children}){
  const { user, setUser } = useApp();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const logout = ()=>{ setUser(null); navigate('/'); setMenuOpen(false); }
  const closeMenu = ()=> setMenuOpen(false);

  return (
    <div className="app-container">
      <nav className="nav">
        <div className="nav-inner">
          <div className="nav-left">
            <Link to={user?.role === 'admin' ? "/dashboard" : "/tables"} className="brand">🍽️ HotelBilling</Link>
            <div className="nav-links">
              <Link to="/tables" onClick={closeMenu}>Tables</Link>
              <Link to="/bills" onClick={closeMenu}>Bills</Link>
              {user && user.role === 'admin' ? <Link to="/menu" onClick={closeMenu}>Admin</Link> : null}
              {user && user.role === 'admin' ? <Link to="/dashboard" onClick={closeMenu}>Dashboard</Link> : null}
            </div>
          </div>

          <div className="nav-right">
            <div className="user-info">
              {user ? <span className="user-name">{user.name} <span className="user-role">({user.role})</span></span> : null}
            </div>
            {user ? <button onClick={logout} className="btn btn-ghost btn-logout">Logout</button> : null}
            {user ? <button onClick={()=>setMenuOpen(!menuOpen)} className="burger-btn" aria-label="Menu">
              <span className={menuOpen ? 'burger-icon open' : 'burger-icon'}>
                <span></span>
                <span></span>
                <span></span>
              </span>
            </button> : null}
          </div>
        </div>
      </nav>

      {menuOpen && <div className="menu-overlay" onClick={closeMenu}></div>}
      
      <div className={menuOpen ? 'mobile-menu open' : 'mobile-menu'}>
        <div className="mobile-menu-header">
          <div className="mobile-user-info">
            <div className="user-name-mobile">{user?.name}</div>
            <div className="user-role-mobile">{user?.role}</div>
          </div>
          <button onClick={closeMenu} className="close-btn">×</button>
        </div>
        <nav className="mobile-nav">
          <Link to="/tables" onClick={closeMenu} className="mobile-nav-link">📋 Tables</Link>
          <Link to="/bills" onClick={closeMenu} className="mobile-nav-link">🧾 Bills</Link>
          {user && user.role === 'admin' ? <Link to="/menu" onClick={closeMenu} className="mobile-nav-link">⚙️ Admin</Link> : null}
          {user && user.role === 'admin' ? <Link to="/dashboard" onClick={closeMenu} className="mobile-nav-link">📊 Dashboard</Link> : null}
        </nav>
        <div className="mobile-menu-footer">
          <button onClick={logout} className="btn btn-danger" style={{width:'100%'}}>Logout</button>
        </div>
      </div>

      <main className="main-content">{children}</main>
    </div>
  )
}

/* -------------------- Tables Page -------------------- */
function TablesPage(){
  const { tables } = useApp();
  const [selected, setSelected] = useState(null);

  // NOTE: order swapped here so details (menu + bill) appear LEFT, and tables ICONS on the RIGHT.
  return (
    <div className="page-grid">
      <div className="details-section">
        <h2 className="h2">Table Details</h2>
        {selected ? <TableDetail table={selected} /> : <div className="card"><p className="muted">Select a table to manage bills</p></div>}
      </div>

      <div className="tables-section">
        <h2 className="h2">Tables</h2>
        <div className="tables-grid">
          {tables.map(t=> (
            <button key={t.id} className="table-card" onClick={()=>setSelected(t)}>
              <div className="table-card-header">
                <div className="table-name">{t.name}</div>
                <div className="table-id">{t.id}</div>
              </div>
              <div className={t.currentBillId ? 'status-badge active' : 'status-badge free'}>
                {t.currentBillId ? '● Active Bill' : '○ Available'}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

/* -------------------- Updated TableDetail Component -------------------- */
function TableDetail({table}) {
  const { createBill, menu, changeItemQty, bills, waiters, finalizeBill } = useApp();
  const [billId, setBillId] = useState(table.currentBillId || null);
  const [waiterName, setWaiterName] = useState(waiters[0]?.name || '');

  useEffect(()=>{ setBillId(table.currentBillId || null); }, [table]);
  useEffect(()=>{ if(!waiterName && waiters[0]) setWaiterName(waiters[0].name); }, [waiters]);

  const startBill = ()=>{ 
    if(!waiterName) return alert('Please select a waiter'); 
    const id = createBill({tableId: table.id, waiterName}); 
    setBillId(id); 
  }

  const inc = (menuItem) => {
    if(!billId) return alert('Create a bill first');
    changeItemQty(billId, menuItem.id, +1);
  }
  const dec = (menuItem) => {
    if(!billId) return alert('Create a bill first');
    changeItemQty(billId, menuItem.id, -1);
  }

  const bill = bills.find(b=>b.id===billId);

  const subtotal = bill?.items?.reduce((s,i)=> s + i.price * i.qty, 0) || 0;
  const gstTotal = bill?.items?.reduce((s,i)=> s + i.price * i.qty * i.gst, 0) || 0;
  const total = subtotal + gstTotal;

  return (
    <div className="card table-detail-card">
      <div className="card-header">
        <div>
          <div className="table-detail-name">{table.name}</div>
          <div className="table-detail-id">{table.id}</div>
        </div>
      </div>

      <label className="label">Waiter</label>
      <select value={waiterName} onChange={e=>setWaiterName(e.target.value)} className="select">
        {waiters.map(w=> <option key={w.id} value={w.name}>{w.name}</option>)}
      </select>

      {!billId ? (
        <button onClick={startBill} className="btn btn-primary create-bill-btn">Create Bill</button>
      ) : (
        <div className="active-bill-info">Active bill: <span>{billId}</span></div>
      )}

      <div className="table-layout">
        {/* LEFT: menu grid */}
        <div className="menu-panel">
          <h4 className="h3">Menu</h4>
          <div className="menu-grid">
            {menu.map(it=> {
              const existing = bill?.items?.find(x=>x.id===it.id);
              const qty = existing ? existing.qty : 0;
              return (
                <div key={it.id} className="menu-card">
                  <div className="menu-card-top">
                    <div className="menu-card-title">{it.name}</div>
                    <div className="menu-card-price">₹{it.price}</div>
                  </div>

                  <div className="menu-card-bottom">
                    <div className="menu-gst">GST {Math.round(it.gst*100)}%</div>
                    <div className="qty-controls">
                      <button className="qty-btn" onClick={()=>dec(it)} aria-label="decrease">−</button>
                      <div className="qty-display">{qty}</div>
                      <button className="qty-btn" onClick={()=>inc(it)} aria-label="increase">+</button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* RIGHT: bill summary */}
        <div className="bill-panel">
          <h4 className="h3">Bill Items</h4>
          <div className="bill-items-panel">
            {(!bill || (bill.items && bill.items.length === 0)) ? (
              <p className="muted">No items yet</p>
            ) : (
              bill.items.map(i=> (
                <div key={i.id} className="bill-row bill-row-detailed">
                  <div className="bill-left">
                    <div className="item-name">{i.name}</div>
                    <div className="item-detail">{i.qty} × ₹{i.price} • GST {Math.round(i.gst*100)}%</div>
                  </div>
                  <div className="bill-right">
                    <div className="item-total">₹{(i.price*i.qty).toFixed(2)}</div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="bill-summary-inline">
            <div><span className="muted">Subtotal</span><strong>₹{subtotal.toFixed(2)}</strong></div>
            <div><span className="muted">GST</span><strong>₹{gstTotal.toFixed(2)}</strong></div>
            <div className="summary-divider"></div>
            <div className="total-row"><strong>Total</strong><strong>₹{total.toFixed(2)}</strong></div>
          </div>

          <div className="bill-actions-panel">
            {bill && !bill.paid && <button className="btn btn-primary" onClick={()=>finalizeBill(bill.id)}>Finalize & Pay</button>}
            {(!bill || bill.items.length===0) ? null : <Link to={`/bill/${bill?.id}`} className="btn btn-outline">View Full Bill</Link>}
          </div>
        </div>
      </div>
    </div>
  );
}

/* -------------------- Bills Page -------------------- */
function BillsPage(){
  const { bills, finalizeBill } = useApp();
  return (
    <div className="bills-container">
      <h2 className="h2">Bills & History</h2>
      <div className="bills-list">
        {bills.length===0 ? (
          <div className="card"><p className="muted">No bills yet</p></div>
        ) : (
          bills.map(b=> (
            <div key={b.id} className="card bill-card">
              <div className="bill-card-header">
                <div>
                  <div className="bill-id">{b.id}</div>
                  <div className="bill-meta">Waiter: {b.waiterName} • Table: {b.tableId}</div>
                  <div className="bill-time">{new Date(b.createdAt).toLocaleString()}</div>
                </div>
                <div className={b.paid ? 'badge-paid' : 'badge-pending'}>
                  {b.paid ? 'Paid' : 'Pending'}
                </div>
              </div>
              <div className="bill-actions">
                <Link to={`/bill/${b.id}`} className="btn btn-outline">View Bill</Link>
                {!b.paid && <button onClick={()=>finalizeBill(b.id)} className="btn btn-primary">Finalize</button>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

/* -------------------- Bill View -------------------- */
function BillView(){
  const { bills } = useApp();
  const { id } = useParams();
  const bill = bills.find(b=>b.id===id);
  if(!bill) return <div className="card"><p className="muted">Bill not found</p></div>;

  const subtotal = bill.items.reduce((s,i)=>s + i.price * i.qty, 0);
  const gstTotal = bill.items.reduce((s,i)=> s + i.price*i.qty*i.gst, 0);
  const total = subtotal + gstTotal;

  return (
    <div className="bill-view">
      <div className="card">
        <div className="bill-view-header">
          <div>
            <h2 className="bill-id-large">{bill.id}</h2>
            <div className="bill-meta">Waiter: {bill.waiterName} • Table: {bill.tableId}</div>
            <div className="bill-time">{new Date(bill.createdAt).toLocaleString()}</div>
          </div>
          <div className={bill.paid ? 'badge-paid' : 'badge-pending'}>
            {bill.paid ? 'Paid' : 'Pending'}
          </div>
        </div>

        <div className="bill-items-detail">
          <h4 className="section-title">ITEMS</h4>
          {bill.items.map(it=> (
            <div key={it.id} className="bill-detail-row">
              <div>
                <div className="item-name">{it.name}</div>
                <div className="item-detail">{it.qty} × ₹{it.price} (GST {Math.round(it.gst*100)}%)</div>
              </div>
              <div className="item-total">₹{(it.price*it.qty).toFixed(2)}</div>
            </div>
          ))}
        </div>

        <div className="bill-summary">
          <div className="summary-row">
            <span>Subtotal</span>
            <span>₹{subtotal.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>GST</span>
            <span>₹{gstTotal.toFixed(2)}</span>
          </div>
          <div className="summary-divider"></div>
          <div className="summary-row total">
            <span>Total</span>
            <span>₹{total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* -------------------- Menu Admin Page -------------------- */
function MenuAdminPage(){
  const { menu, addMenuItem, updateMenuItem, deleteMenuItem, addTable, waiters, addWaiter, users, addUser } = useApp();
  const [form, setForm] = useState({name:'', price:'', gst:'0.05'});
  const [newUser, setNewUser] = useState({id:'', name:'', role:'staff', password:''});

  const onAdd = (e)=>{ 
    e.preventDefault(); 
    if(!form.name || !form.price) return alert('fill name and price'); 
    addMenuItem({ id: `m${Date.now()}`, name: form.name, price: Number(form.price), gst: Number(form.gst) }); 
    setForm({name:'', price:'', gst:'0.05'}); 
  }
  
  const onAddUser = (e)=>{ 
    e.preventDefault(); 
    if(!newUser.id || !newUser.password || !newUser.name) return alert('fill all fields'); 
    const res = addUser(newUser); 
    if(!res.ok) return alert(res.msg); 
    setNewUser({id:'', name:'', role:'staff', password:''}); 
  }

  return (
    <div className="admin-grid">
      <div className="admin-section">
        <div className="card">
          <h3 className="h3">Menu Management</h3>
          <form onSubmit={onAdd} className="form">
            <label className="label">Item Name</label>
            <input placeholder="e.g., Margherita Pizza" value={form.name} onChange={e=>setForm(f=>({...f, name:e.target.value}))} className="input" />
            <label className="label">Price (₹)</label>
            <input type="number" placeholder="e.g., 250" value={form.price} onChange={e=>setForm(f=>({...f, price:e.target.value}))} className="input" />
            <label className="label">GST Rate</label>
            <select value={form.gst} onChange={e=>setForm(f=>({...f, gst:e.target.value}))} className="select">
              <option value="0">0%</option>
              <option value="0.05">5%</option>
              <option value="0.12">12%</option>
              <option value="0.18">18%</option>
            </select>
            <button className="btn btn-primary" style={{width:'100%'}}>Add Menu Item</button>
          </form>

          <div className="menu-items-list">
            <h4 className="h4">Existing Items</h4>
            {menu.map(it=> (
              <div key={it.id} className="menu-item">
                <div className="menu-item-info">
                  <div className="menu-item-name">{it.name}</div>
                  <div className="menu-item-price">₹{it.price} • GST {Math.round(it.gst*100)}%</div>
                </div>
                <div className="menu-item-actions">
                  <button onClick={()=>updateMenuItem(it.id, {name: it.name + ' ★'})} className="btn btn-sm btn-ghost">Edit</button>
                  <button onClick={()=>deleteMenuItem(it.id)} className="btn btn-sm btn-danger">Delete</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="admin-section">
        <div className="card">
          <h3 className="h3">Add Table</h3>
          <AddTableForm onAdd={(name)=>addTable(name)} />
        </div>

        <div className="card">
          <h3 className="h3">Add Waiter</h3>
          <AddWaiterForm onAdd={(name)=>addWaiter(name)} />
          <div className="waiter-list">
            {waiters.map(w=> <div key={w.id} className="list-item">{w.name}</div>)}
          </div>
        </div>

        <div className="card">
          <h3 className="h3">Add User</h3>
          <form onSubmit={onAddUser} className="form">
            <input placeholder="User ID (login)" value={newUser.id} onChange={e=>setNewUser(u=>({...u, id:e.target.value}))} className="input" />
            <input placeholder="Display name" value={newUser.name} onChange={e=>setNewUser(u=>({...u, name:e.target.value}))} className="input" />
            <select value={newUser.role} onChange={e=>setNewUser(u=>({...u, role:e.target.value}))} className="select">
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </select>
            <input type="password" placeholder="Password" value={newUser.password} onChange={e=>setNewUser(u=>({...u, password:e.target.value}))} className="input" />
            <button className="btn btn-primary" style={{width:'100%'}}>Add User</button>
          </form>
          <div className="user-list">
            <h4 className="h4">Users</h4>
            {users.map(u=> <div key={u.id} className="list-item">{u.id} • {u.name} • {u.role}</div>)}
          </div>
        </div>
      </div>
    </div>
  )
}

function AddTableForm({onAdd}){ 
  const [val, setVal] = useState(''); 
  return ( 
    <form onSubmit={(e)=>{e.preventDefault(); if(val) onAdd(val); setVal('');}} className="inline-form">
      <input placeholder="Table name" value={val} onChange={e=>setVal(e.target.value)} className="input" />
      <button className="btn btn-primary">Add</button>
    </form> 
  )
}
function AddWaiterForm({onAdd}){ 
  const [val, setVal] = useState(''); 
  return ( 
    <form onSubmit={(e)=>{e.preventDefault(); if(val) onAdd(val); setVal('');}} className="inline-form">
      <input placeholder="Waiter name" value={val} onChange={e=>setVal(e.target.value)} className="input" />
      <button className="btn btn-primary">Add</button>
    </form> 
  )
}

/* -------------------- Root App -------------------- */
export default function App(){
  return (
    <Router>
      <AppProvider>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/tables" element={<RequireAuth><Layout><TablesPage /></Layout></RequireAuth>} />
          <Route path="/bills" element={<RequireAuth><Layout><BillsPage /></Layout></RequireAuth>} />
          <Route path="/bill/:id" element={<RequireAuth><Layout><BillView /></Layout></RequireAuth>} />
          <Route path="/menu" element={<RequireAdmin><Layout><MenuAdminPage /></Layout></RequireAdmin>} />
          <Route path="/dashboard" element={<RequireAdmin><Layout><Dashboard /></Layout></RequireAdmin>} />
        </Routes>
      </AppProvider>
    </Router>
  )
}

function RequireAuth({children}){ const { user } = useApp(); if(!user) return <Navigate to='/' />; return children; }
function RequireAdmin({children}){ const { user } = useApp(); if(!user) return <Navigate to='/' />; if(user.role !== 'admin') return <Navigate to='/tables' />; return children; }
