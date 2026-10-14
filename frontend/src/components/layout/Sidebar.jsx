const navigationItems = [
  {
    id: "overview",
    label: "Overview",
    icon: "⌂",
  },
  {
    id: "warband",
    label: "My Warband",
    icon: "⚔",
  },
  {
    id: "settings",
    label: "Settings",
    icon: "⚙",
  },
];

function Sidebar({ isExpanded, onToggle, activeItem, onNavigate }) {
  return (
    <aside
      className={`app-sidebar ${isExpanded ? "expanded" : "collapsed"}`}
      aria-label="Main navigation"
    >
      <button
        className="sidebar-toggle"
        type="button"
        onClick={onToggle}
        aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
        aria-expanded={isExpanded}
      >
        <span aria-hidden="true">{isExpanded ? "‹" : "›"}</span>
      </button>

      <nav className="sidebar-navigation">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-link ${activeItem === item.id ? "active" : ""}`}
            type="button"
            onClick={() => onNavigate(item.id)}
            aria-current={activeItem === item.id ? "page" : undefined}
            title={!isExpanded ? item.label : undefined}
          >
            <span className="sidebar-icon" aria-hidden="true">
              {item.icon}
            </span>

            {isExpanded && <span className="sidebar-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="sidebar-status" aria-hidden="true" />
        {isExpanded && <span>Warband HQ</span>}
      </div>
    </aside>
  );
}

export default Sidebar;
