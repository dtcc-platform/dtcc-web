// Maximum file size: 20MB
const MAX_FILE_SIZE = 20 * 1024 * 1024

// Maximum dimension: 4096px (prevents memory exhaustion)
const MAX_DIMENSION = 4096

/**
 * Converts an image File to WebP format using Canvas API
 * @param {File} file - The image file to convert
 * @param {number} quality - WebP quality (0-1), default 0.85
 * @returns {Promise<File>} - Promise that resolves to WebP File object
 */
export async function convertToWebP(file, quality = 0.85) {
  // Feature detection: Check if browser supports canvas.toBlob
  if (!HTMLCanvasElement.prototype.toBlob) {
    console.warn('Browser does not support canvas.toBlob, skipping WebP conversion')
    return file
  }

  // File size validation: Reject files larger than 20MB
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`File size (${(file.size / 1024 / 1024).toFixed(1)}MB) exceeds 20MB limit`)
  }

  // Skip conversion for GIF (preserve animation) or if already WebP
  const fileType = file.type.toLowerCase()
  if (fileType === 'image/gif' || fileType === 'image/webp') {
    return file
  }

  // Only convert common raster formats
  if (!fileType.startsWith('image/')) {
    return file
  }

  return new Promise((resolve, reject) => {
    // Create image element to load the file
    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      try {
        // Get original dimensions
        let width = img.naturalWidth
        let height = img.naturalHeight

        // Downscale if dimensions exceed MAX_DIMENSION
        if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
          const scale = MAX_DIMENSION / Math.max(width, height)
          width = Math.floor(width * scale)
          height = Math.floor(height * scale)
          console.log(`Image downscaled from ${img.naturalWidth}×${img.naturalHeight} to ${width}×${height}`)
        }

        // Create canvas with appropriate dimensions
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height

        // Get 2D context with validation
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          URL.revokeObjectURL(url)
          reject(new Error('Could not get 2D canvas context'))
          return
        }

        // Draw image to canvas (scaled if necessary)
        ctx.drawImage(img, 0, 0, width, height)

        // Convert to WebP blob
        canvas.toBlob(
          (blob) => {
            // Clean up
            URL.revokeObjectURL(url)

            if (!blob) {
              reject(new Error('Canvas toBlob failed'))
              return
            }

            // Create new File from blob with .webp extension
            const originalName = file.name || 'image'
            const nameWithoutExt = originalName.replace(/\.[^.]+$/, '')
            const webpFile = new File([blob], `${nameWithoutExt}.webp`, {
              type: 'image/webp',
              lastModified: Date.now(),
            })

            resolve(webpFile)
          },
          'image/webp',
          quality
        )
      } catch (error) {
        URL.revokeObjectURL(url)
        reject(error)
      }
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Failed to load image'))
    }

    img.src = url
  })
}
