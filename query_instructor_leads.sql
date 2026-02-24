SELECT l.id, l.contact_name, l.contact_phone, l.message, l.created_at, l.status
FROM marketplace_lead l
JOIN marketplace_instructorprofile i ON l.instructor_id = i.id
WHERE i.id = 1 AND l.status = 'CONTACTED'
ORDER BY l.created_at DESC;
