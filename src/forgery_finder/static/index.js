const fakeDelayOnError = 800;
const maxImageSize = 0x2_00_00;
const extraImageScale = 1.4; // Picked manually.
const imageMimeType = 'image/png';

const errorDescriptions = {
    413: 'The uploaded file was too large. Please try again with a smaller file.',
};

const image = document.createElement('img');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');

canvas.width = Math.trunc(250 * extraImageScale);
canvas.height = Math.trunc(160 * extraImageScale);

/**
 * @template {Element} T
 * @param {string} selector
 * @param {new (...args: any) => T} type
 */
function $(selector, type) {
    const value = document.querySelector(selector);

    if (!(value instanceof type)) {
        throw new TypeError(`Element ${selector} is not of type ${type.name}`);
    }

    return value;
}

/**
 * @param {EventTarget} target
 * @param {string} event
 * @returns {Promise<void>}
 */
async function once(target, event) {
    return new Promise((resolve) => {
        target.addEventListener(event, () => resolve(), {once: true});
    });
}

/**
 * @param {number} delay
 * @returns {Promise<void>}
 */
async function timeout(delay) {
    return new Promise((resolve) => {
        setTimeout(resolve, delay);
    });
}

/**
 * @param {HTMLCanvasElement} canvas
 * @returns {Promise<Blob | null>}
 */
async function canvasToBlob(canvas) {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        }, imageMimeType);
    });
}

/**
 * @template T
 */
async function request(form, submitter, progressBar) {
    const animationend = once(progressBar, 'animationend');
    const body = new FormData(form, submitter);

    const file = body.get('file_upload');

    if (file instanceof File && file.size > maxImageSize && context) {
        const load = once(image, 'load');
        const url = URL.createObjectURL(file);

        image.src = url;
        await load;
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        URL.revokeObjectURL(url);

        const blob = await canvasToBlob(canvas);

        if (blob && blob.size < file.size) {
            body.set('file_upload', blob);
            console.debug(
                'File size reduced from',
                file.size.toLocaleString('en-US', {
                    style: 'unit',
                    unit: 'byte',
                }),
                'to',
                blob.size.toLocaleString('en-US', {
                    style: 'unit',
                    unit: 'byte',
                }),
            );
        }
    }

    const request = await fetch(form.action, {
        mode: 'same-origin',
        method: form.method,
        body,
        headers: {
            Accept: 'application/json',
        },
    });

    /**
     * @type {T | {
     *   error: string;
     *   code?: number | null;
     *   description?: string | null;
     * }}
     */
    let result;

    if (request.headers.get('Content-Type') === 'application/json') {
        result = await request.json();
    } else {
        result = {
            error: `${request.status} ${request.statusText}`,
            code: request.status,
            description:
                errorDescriptions[request.status] ??
                'Something has gone wrong. Please try again later.',
        };
    }

    await (request.ok ? animationend : timeout(fakeDelayOnError));

    return result;
}

const verification = {
    form: $('#verify', HTMLFormElement),
    progress: $('#verify_progress', HTMLDivElement),
    animation: $('#verify_progress_bar', HTMLDivElement),
    result: $('#verify_result', HTMLDivElement),
    back: $('#verify_back', HTMLButtonElement),
    score: $('#score', HTMLSpanElement),
    uploaded: $('#uploaded', HTMLImageElement),
    original: $('#original', HTMLImageElement),
    diff: $('#diff', HTMLImageElement),
    threshold: $('#threshold', HTMLImageElement),
};

const upload = {
    form: $('#upload', HTMLFormElement),
    progress: $('#upload_progress', HTMLDivElement),
    animation: $('#upload_progress_bar', HTMLDivElement),
    result: $('#upload_result', HTMLDivElement),
};

const error = {
    page: $('#error', HTMLDivElement),
    back: $('#error_back', HTMLButtonElement),
    title: $('#error_title', HTMLHeadingElement),
    desc: $('#error_desc', HTMLParagraphElement),
};

verification.form.addEventListener('submit', async (event) => {
    event.preventDefault();

    verification.form.hidden = true;
    upload.form.hidden = true;
    verification.progress.hidden = false;
    verification.result.hidden = true;

    /**
     * @type {{
     *   score: number;
     *   uploaded: string;
     *   original: string;
     *   diff: string;
     *   threshold: string;
     * } | {
     *   error: string;
     *   code?: number | null;
     *   description?: string | null;
     * }}
     */
    const result = await request(
        verification.form,
        event.submitter,
        verification.animation,
    );

    if ('error' in result) {
        error.title.textContent = result.error;
        error.desc.textContent = result.description ?? '';

        verification.progress.hidden = true;
        error.page.hidden = false;
    } else {
        verification.score.textContent = String(result.score);
        verification.uploaded.src = result.uploaded;
        verification.original.src = result.original;
        verification.diff.src = result.diff;
        verification.threshold.src = result.threshold;

        verification.progress.hidden = true;
        verification.result.hidden = false;
    }
});

verification.back.addEventListener('click', () => {
    verification.form.hidden = false;
    verification.result.hidden = true;
    upload.form.hidden = false;
    upload.result.hidden = true;
});

upload.form.addEventListener('submit', async (event) => {
    event.preventDefault();

    verification.form.hidden = true;
    upload.form.hidden = true;
    upload.progress.hidden = false;
    upload.result.hidden = true;
    /**
     * @type {{
     *   ok: true;
     * } | {
     *   error: string;
     *   code?: number | null;
     *   description?: string | null;
     * }}
     */
    const result = await request(
        upload.form,
        event.submitter,
        upload.animation,
    );

    if ('error' in result) {
        error.title.textContent = result.error;
        error.desc.textContent = result.description ?? '';

        upload.progress.hidden = true;
        error.page.hidden = false;
    } else {
        verification.form.hidden = false;
        verification.result.hidden = true;
        upload.form.hidden = false;
        upload.result.hidden = false;
        upload.progress.hidden = true;
    }
});

error.back.addEventListener('click', () => {
    verification.form.hidden = false;
    verification.result.hidden = true;
    upload.form.hidden = false;
    upload.result.hidden = true;
    error.page.hidden = true;
});
