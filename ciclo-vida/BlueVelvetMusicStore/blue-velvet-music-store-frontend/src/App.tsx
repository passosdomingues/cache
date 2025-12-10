/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Root component defining routes and layout with cart provider.
 * @us US-0000 Project Configuration - Granularity: Routing
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import NavigationBar from './components/NavigationBar';
import SidebarMenu from './components/SidebarMenu';
import HomePage from './pages/HomePage';
import ProductListPage from './pages/ProductListPage';
import ProductFormPage from './pages/ProductFormPage';
import CategoryListPage from './pages/CategoryListPage';
import CategoryFormPage from './pages/CategoryFormPage';
import GiftCardPage from './pages/GiftCardPage';
import LoginPage from './pages/LoginPage';
import CartPage from './pages/CartPage';
import './styles/App.css';

function App() {
  return (
    <CartProvider>
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
                <Route path="/categories/new" element={<CategoryFormPage />} />
                <Route path="/categories/:id/edit" element={<CategoryFormPage />} />
                <Route path="/categories/:categoryId/products" element={<ProductListPage />} />
                <Route path="/giftcards" element={<GiftCardPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/cart" element={<CartPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </CartProvider>
  );
}

export default App;
