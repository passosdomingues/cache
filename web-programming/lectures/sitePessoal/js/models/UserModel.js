/**
 * @file Modelo do usuário (Rafael)
 * @brief Gerencia dados pessoais e de contato
 */

class UserModel {
    constructor() {
        this.userData = {
            name: "Rafael Passos Domingues",
            title: "Físico & Cientista da Computação",
            summary: "Com formação em Física pela UNIFAL-MG (2014-2018) e atualmente cursando Ciência da Computação (2023-2029). Experiência em astrofísica galáctica, educação, empreendedorismo e inovação tecnológica.",
            profileImage: "assets/images/profile.jpg",
            contact: {
                email: "rafaelpassosdomingues@gmail.com",
                github: "https://github.com/passosdomingues",
                linkedin: "https://www.linkedin.com/in/rafaelpassosdomingues/",
                instagram: "@rafaelpassosdomingues",
                site: "https://sites.google.com/view/pandefisica/"
            },
            education: [
                {
                    degree: "Bacharelado em Ciência da Computação",
                    institution: "UNIFAL-MG",
                    period: "2023-2029",
                    status: "Cursando"
                },
                {
                    degree: "Mestrado em Física",
                    institution: "UNIFEI",
                    period: "2021-2023",
                    status: "Concluído"
                },
                {
                    degree: "Bacharelado em Física",
                    institution: "UNIFAL-MG",
                    period: "2014-2018",
                    status: "Concluído"
                }
            ]
        };
    }

    /**
     * @brief Retorna dados do usuário
     * @return {Object} Dados completos do usuário
     */
    getUserData() {
        return this.userData;
    }

    /**
     * @brief Atualiza dados do usuário
     * @param {Object} newData - Novos dados do usuário
     */
    updateUserData(newData) {
        this.userData = { ...this.userData, ...newData };
        return this.userData;
    }
}

export default UserModel;