const navigationItems = [
  { id: "overview", label: "Overview", icon: "⌂" },
  { id: "warband", label: "My Warband", icon: "⚔" },
  { id: "settings", label: "Settings", icon: "⚙" },
];

function MobileMenu({ activeItem, onNavigate, onClose }) {
  const handleNavigate = (page) => {
    onNavigate(page);
    onClose();
  };

  return (
    <aside
      className="mobile-menu"
      id="mobile-navigation"
      aria-label="Mobile navigation"
    >
      <div className="mobile-menu-header">
        <span>Navigation</span>
        <button
          type="button"
          className="mobile-menu-close"
          onClick={onClose}
          aria-label="Close navigation menu"
        >
          ×
        </button>
      </div>

      <nav className="mobile-menu-navigation">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`sidebar-link ${activeItem === item.id ? "active" : ""}`}
            onClick={() => handleNavigate(item.id)}
            aria-current={activeItem === item.id ? "page" : undefined}
          >
            <span className="sidebar-icon" aria-hidden="true">
              {item.icon}
            </span>
            <span className="sidebar-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="mobile-menu-footer">
        <span className="sidebar-status" aria-hidden="true" />
        <span>Warband HQ</span>
      </div>
    </aside>
  );
}

export default MobileMenu;
