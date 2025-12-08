import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import SidebarMenu from './components/SidebarMenu';
import HomePage from './pages/HomePage';
import ProductListPage from './pages/ProductListPage';
import ProductFormPage from './pages/ProductFormPage';
import CategoryListPage from './pages/CategoryListPage';
import LoginPage from './pages/LoginPage';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <NavigationBar />
        <div className="main-container">
          <SidebarMenu />
          <main className="content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products" element={<ProductListPage />} />
              <Route path="/products/new" element={<ProductFormPage />} />
              <Route path="/categories" element={<CategoryListPage />} />
              <Route path="/login" element={<LoginPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
