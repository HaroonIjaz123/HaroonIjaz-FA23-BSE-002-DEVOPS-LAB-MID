import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { validateSubmission } from './validation.js';
import './styles.css';

const emptyForm = { name: '', reg_no: '', title: '', url: '' };

function App() {
  const [form, setForm] = useState(emptyForm);
  const [submissions, setSubmissions] = useState([]);
  const [errors, setErrors] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [apiAvailable, setApiAvailable] = useState(true);

  useEffect(() => {
    fetch('/api/submissions')
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then(setSubmissions)
      .catch(() => {
        setApiAvailable(false);
        try { setSubmissions(JSON.parse(localStorage.getItem('submissions') || '[]')); }
        catch { setSubmissions([]); }
      })
      .finally(() => setLoading(false));
  }, []);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setMessage('');
    const validationErrors = validateSubmission(form);
    setErrors(validationErrors);
    if (validationErrors.length) return;

    setSaving(true);
    try {
      if (!apiAvailable) {
        const next = [...submissions, Object.fromEntries(Object.entries(form).map(([key, value]) => [key, value.trim()]))];
        localStorage.setItem('submissions', JSON.stringify(next));
        setSubmissions(next);
        setForm(emptyForm);
        setErrors([]);
        setMessage('Submission saved in this browser.');
        return;
      }
      const response = await fetch('/api/submissions', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form),
      });
      const result = await response.json();
      if (!response.ok) { setErrors(result.errors ?? [result.error ?? 'Submission failed.']); return; }
      setSubmissions(result.submissions);
      setForm(emptyForm);
      setErrors([]);
      setMessage('Submission saved.');
    } catch {
      setMessage('Could not save your submission. Please try again.');
    } finally { setSaving(false); }
  }

  return <>
    <header><h1>Assignment Submission Portal</h1><p>CSC418 – DevOps · COMSATS University Islamabad, Attock Campus</p></header>
    <main>
      <section className="card">
        <h2>Submit an assignment</h2>
        {errors.length > 0 && <div className="errors" role="alert">{errors.map((error) => <div className="error" key={error}>{error}</div>)}</div>}
        {message && <p className="status" role="status">{message}</p>}
        <form onSubmit={submit} noValidate>
          <div className="grid">
            <Field label="Name" name="name" placeholder="e.g. Haroon Ijaz" value={form.name} onChange={update} />
            <Field label="Registration Number" name="reg_no" placeholder="e.g. FA23-BSE-002" value={form.reg_no} onChange={update} />
            <Field className="full" label="Assignment Title" name="title" placeholder="e.g. Lab Assignment 2" value={form.title} onChange={update} />
            <Field className="full" label="Submission URL" name="url" placeholder="https://github.com/username/repository" value={form.url} onChange={update} />
          </div>
          <button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Submit'}</button>
        </form>
      </section>
      <section className="card">
        <h2>Saved Submissions <span className="badge">{submissions.length}</span></h2>
        <div className="table-wrap"><table id="submissions">
          <thead><tr><th>Name</th><th>Reg. No</th><th>Assignment</th><th>URL</th></tr></thead>
          <tbody>{loading ? <tr><td className="empty" colSpan="4">Loading submissions…</td></tr> : submissions.length ? submissions.map((item, index) => <tr key={`${item.reg_no}-${index}`}>
            <td data-label="Name">{item.name}</td><td data-label="Reg. No">{item.reg_no}</td><td data-label="Assignment">{item.title}</td>
            <td data-label="URL"><a href={item.url} target="_blank" rel="noopener noreferrer">{item.url}</a></td>
          </tr>) : <tr><td className="empty" colSpan="4">No submissions yet. Be the first to submit.</td></tr>}</tbody>
        </table></div>
      </section>
    </main>
    <footer>Haroon Ijaz · FA23-BSE-002 · CSC418 Lab Midterm</footer>
  </>;
}

function Field({ label, name, className = '', ...props }) {
  return <div className={className}><label htmlFor={name}>{label}</label><input id={name} name={name} {...props} /></div>;
}

createRoot(document.getElementById('root')).render(<App />);
