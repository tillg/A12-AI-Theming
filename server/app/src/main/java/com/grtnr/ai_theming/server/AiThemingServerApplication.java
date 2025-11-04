package com.grtnr.ai_theming.server;

import com.mgmtp.a12.dataservices.DataServicesApplication;
import org.springframework.boot.SpringApplication;

@DataServicesApplication(scanBasePackages = {DataServicesApplication.DATASERVICES_BASE_PACKAGE,
        "com.grtnr.ai_theming.server"})
public class AiThemingServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(AiThemingServerApplication.class, args);
    }
}
