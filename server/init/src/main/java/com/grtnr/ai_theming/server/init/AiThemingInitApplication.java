package com.grtnr.ai_theming.server.init;

import com.mgmtp.a12.dataservices.DataServicesApplication;
import com.mgmtp.a12.dataservices.init.app.InitAppApplication;

@DataServicesApplication(scanBasePackages = {
        DataServicesApplication.DATASERVICES_BASE_PACKAGE,
        "com.grtnr.ai_theming.server.init"
})
public class AiThemingInitApplication {
    public static void main(String[] args) {
        InitAppApplication.run(args, AiThemingInitApplication.class);
    }
}
