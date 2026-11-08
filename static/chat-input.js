'use strict';
document.addEventListener('keydown', event => {
 const input = event.target;
 if (!(input instanceof HTMLTextAreaElement) || input.id !== 'question') return;
 if (event.key !== 'Enter' || event.shiftKey || event.isComposing || event.keyCode === 229) return;
 event.preventDefault();
 const form = input.form;
 if (!form || input.disabled || !input.value.trim()) return;
 const submit = form.querySelector('button[type="submit"], button.send');
 if (submit?.disabled) return;
 form.requestSubmit();
});
