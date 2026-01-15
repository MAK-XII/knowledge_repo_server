# Knowledge Repository - Database & Server

## Database Schema

### Tables

#### `categories`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Category name (unique) |
| description | TEXT | Optional description |
| created_at | DATETIME | Creation timestamp |

#### `departments`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Department name (unique) |
| description | TEXT | Optional description |
| created_at | DATETIME | Creation timestamp |

#### `priorities`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Priority name (unique) |
| level | INTEGER | Priority level (higher = more urgent) |
| color | TEXT | Color code for UI display |
| created_at | DATETIME | Creation timestamp |

#### `tags`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Tag name (unique) |
| created_at | DATETIME | Creation timestamp |

#### `articles`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Article title |
| summary | TEXT | Short summary |
| content | TEXT | Full HTML content |
| category_id | INTEGER | Foreign key to categories |
| department_id | INTEGER | Foreign key to departments |
| priority_id | INTEGER | Foreign key to priorities |
| author | TEXT | Author name |
| views | INTEGER | View counter |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

#### `article_tags` (Junction Table)
| Column | Type | Description |
|--------|------|-------------|
| article_id | INTEGER | Foreign key to articles |
| tag_id | INTEGER | Foreign key to tags |

#### `attachments`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| article_id | INTEGER | Foreign key to articles (nullable) |
| file_name | TEXT | Original filename |
| mime_type | TEXT | File MIME type |
| size | INTEGER | File size in bytes |
| url | TEXT | S3/cloud storage URL |
| created_at | DATETIME | Creation timestamp |

### Full-Text Search
The database includes an FTS5 virtual table `articles_fts` for fast full-text search across article titles, summaries, and content.

## Environment Variables

Set these before starting the server for S3/cloud storage support:

| Variable | Required | Description |
|----------|----------|-------------|
| `S3_BUCKET` | Yes | S3 bucket name |
| `S3_REGION` | No | AWS region (default: us-east-1) |
| `S3_ENDPOINT` | No | Custom endpoint for MinIO/R2 |
| `S3_ACCESS_KEY_ID` | Yes | AWS access key |
| `S3_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `PORT` | No | Server port (default: 3000) |

## API Endpoints

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create category
- `PUT /api/categories/:id` - Update category
- `DELETE /api/categories/:id` - Delete category

### Departments
- `GET /api/departments` - Get all departments
- `POST /api/departments` - Create department
- `PUT /api/departments/:id` - Update department
- `DELETE /api/departments/:id` - Delete department

### Priorities
- `GET /api/priorities` - Get all priorities
- `POST /api/priorities` - Create priority
- `PUT /api/priorities/:id` - Update priority
- `DELETE /api/priorities/:id` - Delete priority

### Tags
- `GET /api/tags` - Get all tags
- `POST /api/tags` - Create tag
- `DELETE /api/tags/:id` - Delete tag

### Articles
- `GET /api/articles` - Get all articles (with optional filters)
- `GET /api/articles/search?q=query` - Full-text search
- `GET /api/articles/stats` - Get statistics
- `GET /api/articles/:id` - Get single article
- `POST /api/articles` - Create article
- `PUT /api/articles/:id` - Update article
- `DELETE /api/articles/:id` - Delete article

### Attachments
- `POST /api/attachments` - Upload file attachment (form-data with `file` field)
  - Optional: `articleId` to pre-link attachment to an article
  - Returns: `{ id, file_name, mime_type, size, url }`
  - Max size: 20MB

### Images (Inline)
- `POST /api/images` - Upload inline image for article content (form-data with `file` field)
  - Returns: `{ url, fileName, mimeType, size }`
  - Max size: 10MB
  - Only accepts image/* MIME types

## Installation

```bash
cd server
npm install
npm start
```

The server will start at http://localhost:3000

## Example API Usage

### Create an article
```javascript
fetch('/api/articles', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        title: 'My Article',
        summary: 'Brief description',
        content: '<p>Article content here</p>',
        category_id: 1,
        department_id: 2,
        priority_id: 3,
        tags: ['tag1', 'tag2'],
        attachmentIds: [1, 2]  // Link previously uploaded attachments
    })
})
```

### Search articles
```javascript
fetch('/api/articles/search?q=keyword')
    .then(res => res.json())
    .then(articles => console.log(articles))
```

### Filter articles
```javascript
fetch('/api/articles?category_id=1&department_id=2')
    .then(res => res.json())
    .then(articles => console.log(articles))
```

### Upload attachment
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/attachments', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(attachment => {
    console.log('Uploaded:', attachment.url);
    // Use attachment.id when creating/updating article
})
```

### Upload inline image
```javascript
const formData = new FormData();
formData.append('file', imageFile);

fetch('/api/images', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(result => {
    // Insert image into editor content
    const imgHtml = `<img src="${result.url}" alt="...">`;
})
```
