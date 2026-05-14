/* global bootstrap */

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
}

function toggleContactInfo() {
    const checkbox = document.getElementById('id_is_anonymous');
    const container = document.querySelector('.contact-info-container');
    if (!checkbox || !container) {
        return;
    }
    container.style.display = checkbox.checked ? '' : 'none';
}

function init() {
    document.querySelectorAll('.vote').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const questionId = btn.id;
            const response = await fetch(`/q/${questionId}/upvote`, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            const counter = btn.previousElementSibling;
            if (counter) {
                counter.textContent = data.current_vote_count;
            }
            btn.classList.toggle('btn-light');
            btn.classList.toggle('btn-dark');

            // Swap the label to match the new state. Server renders one of two
            // strings on page load; we replicate that toggle client-side.
            const icon = btn.querySelector('i');
            const isVoted = btn.classList.contains('btn-dark');
            btn.textContent = isVoted ? ' Remove the upvote' : ' Upvote';
            if (icon) {
                btn.prepend(icon);
            }
        });
    });

    const pageSelect = document.getElementById('page-select');
    if (pageSelect) {
        pageSelect.addEventListener('change', (event) => {
            window.location = event.target.value;
        });
    }

    const questionForm = document.getElementById('question-form');
    document.querySelectorAll('.reply-button').forEach((btn) => {
        btn.addEventListener('click', () => {
            const answerForm = document.getElementById('answer-form');
            if (questionForm && answerForm) {
                answerForm.setAttribute(
                    'action',
                    `${questionForm.getAttribute('action')}q/${btn.id}/reply`,
                );
            }
        });
    });

    const moderateForm = document.getElementById('moderate-form');
    document.querySelectorAll('.moderate-button').forEach((btn) => {
        btn.addEventListener('click', () => {
            if (moderateForm) {
                moderateForm.setAttribute(
                    'action',
                    `${moderateForm.getAttribute('action')}${btn.id}/rejected`,
                );
            }
        });
    });

    const deleteModal = document.getElementById('DeleteModal');
    const deleteForm = document.getElementById('delete-event-form');
    if (deleteModal && deleteForm) {
        deleteModal.addEventListener('show.bs.modal', (event) => {
            const trigger = event.relatedTarget;
            if (trigger && trigger.dataset.url) {
                deleteForm.setAttribute('action', trigger.dataset.url);
            }
        });
    }

    const anonymousCheckbox = document.getElementById('id_is_anonymous');
    if (anonymousCheckbox) {
        anonymousCheckbox.addEventListener('click', toggleContactInfo);
        toggleContactInfo();
    }

    const logoutBtn = document.getElementById('logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            const form = document.getElementById('logout_form');
            if (form) {
                form.submit();
            }
        });
    }

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            new bootstrap.Tooltip(el);
        }
    });

    document.querySelectorAll('textarea[maxlength]').forEach((textarea) => {
        const max = parseInt(textarea.getAttribute('maxlength'), 10);
        if (!max) {
            return;
        }
        const counter = document.createElement('div');
        counter.className = 'form-text text-end textarea-counter';

        const update = () => {
            const remaining = max - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.classList.toggle('text-danger', remaining < 50);
        };

        // Insert after the .form-floating wrapper (or next to the textarea if not wrapped).
        const anchor = textarea.closest('.form-floating') || textarea;
        anchor.parentNode.insertBefore(counter, anchor.nextSibling);
        update();
        textarea.addEventListener('input', update);
    });

    document.querySelectorAll('select.tom-select').forEach((el) => {
        if (typeof window.TomSelect === 'undefined') {
            return;
        }
        new window.TomSelect(el, {
            plugins: ['remove_button'],
            valueField: 'id',
            labelField: 'text',
            searchField: ['text'],
            preload: 'focus',
            load(query, callback) {
                const url = `${el.dataset.autocompleteUrl}?q=${encodeURIComponent(query)}`;
                fetch(url, { credentials: 'same-origin' })
                    .then((r) => (r.ok ? r.json() : { results: [] }))
                    .then((data) => callback(data.results))
                    .catch(() => callback());
            },
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

export { getCookie };
