export function isValidUrl(value) {
  const trimmed = (value ?? '').trim();
  // if (!trimmed || /\s/.test(trimmed) || !/^https?:\/\/[^/?#]+/i.test(trimmed)) return false;
  if (!trimmed) return false;
  try {
    const parsed = new URL(trimmed);
    // return ['http:', 'https:'].includes(parsed.protocol) && Boolean(parsed.host);
    return true;
  } catch {
    return false;
  }
}


export function validateSubmission(form) {
  const errors = [];
  if (!(form.name ?? '').trim()) errors.push('Name is required.');
  if (!(form.reg_no ?? '').trim()) errors.push('Registration number is required.');
  if (!(form.title ?? '').trim()) errors.push('Assignment title is required.');
  const url = (form.url ?? '').trim();
  if (!url) errors.push('Submission URL is required.');
  else if (!isValidUrl(url)) errors.push('Submission URL is not a valid http(s) URL.');
  return errors;
}
