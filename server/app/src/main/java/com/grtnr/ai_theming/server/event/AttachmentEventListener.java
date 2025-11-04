package com.grtnr.ai_theming.server.event;

import com.mgmtp.a12.dataservices.common.events.CommonDataServicesEventListener;
import com.mgmtp.a12.dataservices.common.events.ContentTypeDetectedEvent;
import com.grtnr.ai_theming.server.attachment.MimeTypeValidator;
import org.springframework.stereotype.Service;

@Service
public class AttachmentEventListener {
    private final MimeTypeValidator mimeTypeValidator;

    public AttachmentEventListener(MimeTypeValidator mimeTypeValidator) {
        this.mimeTypeValidator = mimeTypeValidator;
    }

    @CommonDataServicesEventListener
    public void onContentTypeDetection(ContentTypeDetectedEvent event) {
        mimeTypeValidator.validateMimeType(event.getDetectedMimeType());
    }
}
