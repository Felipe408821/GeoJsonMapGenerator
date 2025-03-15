// Función para extraer el contenido de los elementos
function extractStopLinks() {
    // Selecciona todos los elementos que contienen la información de las paradas
    const stopLinks = document.querySelectorAll('a.Line_stopLink__ZTJKK');

    // Si no hay elementos, muestra un mensaje de error
    if (stopLinks.length === 0) {
        console.error('No se encontraron elementos con la clase Line_stopLink__ZTJKK.');
        return;
    }

    // Crea un array para almacenar el contenido de los elementos
    const stopContents = [];

    // Itera sobre cada elemento y extrae su contenido HTML
    stopLinks.forEach((stopLink) => {
        stopContents.push(stopLink.innerHTML);
    });

    // Si se encontraron elementos, crea el archivo JSON
    if (stopContents.length > 0) {
        // Convierte el array a formato JSON
        const jsonData = JSON.stringify(stopContents, null, 2);

        // Crea un archivo JSON y lo descarga
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'stop_links_content.json';
        a.click();
        URL.revokeObjectURL(url);
    } else {
        console.error('No se encontraron datos válidos.');
    }
}

// Función para esperar a que el contenido esté cargado
function waitForContent() {
    // Intenta extraer los datos cada 500 ms
    const interval = setInterval(() => {
        const stopLinks = document.querySelectorAll('a.Line_stopLink__ZTJKK');
        if (stopLinks.length > 0) {
            // Si se encuentran elementos, extrae los datos y detén el intervalo
            clearInterval(interval);
            extractStopLinks();
        }
    }, 500);
}

// Inicia la espera para el contenido
waitForContent();
