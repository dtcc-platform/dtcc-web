/**
 * Converts an image File to WebP format using Canvas API
 * @param {File} file - The image file to convert
 * @param {number} quality - WebP quality (0-1), default 0.85
 * @returns {Promise<File>} - Promise that resolves to WebP File object
 */
export async function convertToWebP(file, quality = 0.85) {
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
        // Create canvas with same dimensions
        const canvas = document.createElement('canvas')
        canvas.width = img.naturalWidth
        canvas.height = img.naturalHeight

        // Draw image to canvas
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0)

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
