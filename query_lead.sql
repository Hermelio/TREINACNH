SELECT l.id, l.contact_name, l.contact_phone, l.status, i.id as instructor_id, u.first_name, u.last_name 
FROM marketplace_lead l 
JOIN marketplace_instructorprofile i ON l.instructor_id = i.id 
JOIN auth_user u ON i.user_id = u.id 
WHERE l.status = 'CONTACTED';
