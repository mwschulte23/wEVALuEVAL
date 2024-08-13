import yaml


if __name__ == '__main__':
    score = 'happiness'
    with open('wrapper/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    sys_template = config['bolt']['step_one']['score']['system_msg']
    print(sys_template.format(**config['bolt']['step_one']['score'][f'{score}_vars']))