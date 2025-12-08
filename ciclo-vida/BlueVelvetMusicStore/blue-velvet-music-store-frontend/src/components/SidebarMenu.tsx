/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Sidebar menu component.
 * @us US-0000 Project Configuration - Granularity: UI Component
 */
import React from 'react';
import '../styles/SidebarMenu.css';

const SidebarMenu: React.FC = () => {
    return (
        <aside className="sidebar">
            <ul className="sidebar-menu">
                <li className="sidebar-item active">
                    <span>🏠</span> Home
                </li>
                <li className="sidebar-item">
                    <span>🎸</span> Instruments
                </li>
                <li className="sidebar-item">
                    <span>🔊</span> Equipment
                </li>
                <li className="sidebar-item">
                    <span>📂</span> Categories
                </li>
            </ul>
            <div className="sidebar-footer">
                <p>© 2025 Blue Velvet</p>
            </div>
        </aside>
    );
};

export default SidebarMenu;
