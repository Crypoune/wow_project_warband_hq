function ConfirmDialog({
  title,
  message,
  confirmLabel = "Continuer",
  cancelLabel = "Annuler",
  onConfirm,
  onCancel,
}) {
  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      onClick={onCancel}
    >
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <h2 id="confirm-dialog-title">{title}</h2>

        <p className="modal-message">{message}</p>

        <div className="modal-actions">
          <button
            type="button"
            className="modal-button modal-cancel"
            onClick={onCancel}
            autoFocus
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            className="modal-button modal-confirm"
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
