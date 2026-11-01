import { useEffect, useState } from "react";
import { Plus, ListChecks } from "lucide-react";

import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
} from "../../services/taskService.js";

import TaskItem from "./TaskItem.jsx";
import TaskForm from "./TaskForm.jsx";
import DeleteTaskDialog from "./DeleteTaskDialog.jsx";

/**
 * Gère et affiche les tâches associées à un objectif.
 *
 * Ce composant centralise les appels au service API
 * et transmet les actions aux composants enfants.
 *
 * @param {number} goalId - Identifiant de l'objectif.
 */
function TaskList({ goalId }) {
  // Liste des tâches de l'objectif.
  const [tasks, setTasks] = useState([]);

  // États du chargement et des messages.
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Gestion du formulaire de création et modification.
  const [taskFormOpen, setTaskFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Gestion de la suppression.
  const [taskToDelete, setTaskToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Indique si une opération sur une tâche est en cours.
  const [isUpdating, setIsUpdating] = useState(false);

  /**
   * Charge les tâches depuis le backend.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadTasks() {
      setLoading(true);
      setError("");

      try {
        const result = await getTasks(goalId);

        if (!cancelled) {
          setTasks(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Impossible de récupérer les tâches.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadTasks();

    return () => {
      cancelled = true;
    };
  }, [goalId]);

  /**
   * Actualise la liste des tâches après une opération.
   */
  async function refreshTasks() {
    const result = await getTasks(goalId);
    setTasks(result);
  }

  /**
   * Ouvre le formulaire de création.
   */
  function handleCreateTask() {
    setEditingTask(null);
    setError("");
    setSuccess("");
    setTaskFormOpen(true);
  }

  /**
   * Ouvre le formulaire avec les informations d'une tâche.
   */
  function handleEditTask(task) {
    setEditingTask(task);
    setError("");
    setSuccess("");
    setTaskFormOpen(true);
  }

  /**
   * Ferme le formulaire et réinitialise son état.
   */
  function handleCloseTaskForm() {
    if (isSubmitting) return;

    setTaskFormOpen(false);
    setEditingTask(null);
  }

  /**
   * Crée ou modifie une tâche selon le contexte.
   */
  async function handleSaveTask(taskData) {
    if (isSubmitting) return;

    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      if (editingTask) {
        await updateTask(editingTask.id, taskData);
        setSuccess("Tâche modifiée avec succès.");
      } else {
        await createTask(goalId, taskData);
        setSuccess("Tâche créée avec succès.");
      }

      await refreshTasks();

      setTaskFormOpen(false);
      setEditingTask(null);
    } catch (err) {
      setError(err.message || "Impossible d'enregistrer cette tâche.");
    } finally {
      setIsSubmitting(false);
    }
  }

  /**
   * Modifie l'état d'une tâche : terminée ou non terminée.
   */
  async function handleToggleTask(task) {
    if (isUpdating) return;

    setIsUpdating(true);
    setError("");
    setSuccess("");

    try {
      await updateTask(task.id, {
        is_completed: !task.is_completed,
      });

      await refreshTasks();
    } catch (err) {
      setError(err.message || "Impossible de modifier cette tâche.");
    } finally {
      setIsUpdating(false);
    }
  }

  /**
   * Demande confirmation avant de supprimer une tâche.
   */
  function handleAskDeleteTask(task) {
    setTaskToDelete(task);
    setError("");
    setSuccess("");
  }

  /**
   * Annule la suppression.
   */
  function handleCancelDeleteTask() {
    if (isDeleting) return;

    setTaskToDelete(null);
  }

  /**
   * Supprime définitivement une tâche après confirmation.
   */
  async function handleConfirmDeleteTask() {
    if (!taskToDelete || isDeleting) return;

    setIsDeleting(true);
    setError("");
    setSuccess("");

    try {
      await deleteTask(taskToDelete.id);

      setTasks((currentTasks) =>
        currentTasks.filter((task) => task.id !== taskToDelete.id),
      );

      setSuccess("Tâche supprimée avec succès.");
      setTaskToDelete(null);
    } catch (err) {
      setError(err.message || "Impossible de supprimer cette tâche.");
    } finally {
      setIsDeleting(false);
    }
  }

  // Calcule la progression des tâches.
  const completedTasks = tasks.filter((task) => task.is_completed).length;

  return (
    <section className="goal-tasks">
      <div className="goal-tasks-header">
        <div className="goal-tasks-title">
          <ListChecks size={18} aria-hidden="true" />
          <h4>
            Tâches ({completedTasks}/{tasks.length})
          </h4>
        </div>

        <button
          type="button"
          className="goal-tasks-add"
          onClick={handleCreateTask}
          disabled={loading || isSubmitting}
        >
          <Plus size={16} aria-hidden="true" />
          Ajouter
        </button>
      </div>

      {error && (
        <p className="goal-tasks-error" role="alert">
          {error}
        </p>
      )}

      {success && (
        <p className="goal-tasks-success" role="status">
          {success}
        </p>
      )}

      {loading ? (
        <p className="goal-tasks-loading">Chargement des tâches...</p>
      ) : tasks.length > 0 ? (
        <div className="goal-tasks-list">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={handleToggleTask}
              onEdit={handleEditTask}
              onDelete={handleAskDeleteTask}
              isUpdating={isUpdating}
            />
          ))}
        </div>
      ) : (
        <p className="goal-tasks-empty">Aucune tâche pour cet objectif.</p>
      )}

      {taskFormOpen && (
        <TaskForm
          task={editingTask}
          onSubmit={handleSaveTask}
          onCancel={handleCloseTaskForm}
          isSubmitting={isSubmitting}
        />
      )}

      <DeleteTaskDialog
        task={taskToDelete}
        onConfirm={handleConfirmDeleteTask}
        onCancel={handleCancelDeleteTask}
        isDeleting={isDeleting}
      />
    </section>
  );
}

export default TaskList;
