// This is for Poppins font
export const ensureFont = () => {
    if (typeof window !== 'undefined' && 'FontFace' in window) {
        const font = new FontFace(
            'Poppins',
            'url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLGT9Z1xlEA.ttf)'
        );
        return font.load().then(() => {
            document.fonts.add(font);
        });
    }

    throw new Error('browser does not support FontFace');
};
