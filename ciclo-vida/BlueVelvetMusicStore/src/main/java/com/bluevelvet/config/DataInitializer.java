package com.bluevelvet.config;

import com.bluevelvet.auth.Role;
import com.bluevelvet.auth.RoleName;
import com.bluevelvet.auth.RoleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    RoleRepository roleRepository;

    @Override
    public void run(String... args) throws Exception {
        if (roleRepository.count() == 0) {
            roleRepository.save(new Role(RoleName.ROLE_ADMINISTRATOR));
            roleRepository.save(new Role(RoleName.ROLE_SALES_MANAGER));
            roleRepository.save(new Role(RoleName.ROLE_EDITOR));
            roleRepository.save(new Role(RoleName.ROLE_ASSISTANT));
            roleRepository.save(new Role(RoleName.ROLE_SHIPPING_MANAGER));
        }
    }
}
