#!/usr/bin/python

'''
Example

  - name: "Associate Service Graph Template with Contract"
    service_graph_module:
      host: IP ADDRESSS
      username: USER
      password: PWD
      tenant_name: TENAR
      contract_name: CONTRACT
      contract_subject: SUBJECT
      SG_template_name: SERVICE_GRAPH_NAME
      state: STATE (default : present)
      validate_certs: yes or no

Rights Reserved to João Cadavez | Porto | 2020

Contacts : João Cadavez
Linkedin : linkedin.com/in/joaocadavez
GitHub : github.com/JoaoCadavez

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.aci import ACIModule, aci_argument_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        contract=dict(required=True, type='str', aliases=['contract_name']),
        subject=dict(required=True, type='str', aliases=['contract_subject', 'subject_name']),
        tenant=dict(required=True, type='str', aliases=['tenant_name']),
        SG=dict(required=True, type='str', aliases=['SG_template_name']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['contract', 'subject', 'tenant', 'SG']],
            ['state', 'present', ['contract', 'subject', 'tenant', 'SG']],
        ],
    )

    contract = module.params['contract']
    subject = module.params['subject']
    tenant = module.params['tenant']
    state = module.params['state']
    SG = module.params['SG']

    aci = ACIModule(module)
    
    aci.construct_url(
        root_class=dict(
            aci_class='fvTenant',
            aci_rn='tn-{0}'.format(tenant),
            module_object=tenant,
            target_filter={'name': tenant},
        ),
        subclass_1=dict(
            aci_class='vzBrCP',
            aci_rn='brc-{0}'.format(contract),
            module_object=contract,
            target_filter={'name': contract},
        ),
        subclass_2=dict(
            aci_class='vzSubj',
            aci_rn='subj-{0}'.format(subject),
            module_object=subject,
            target_filter={'name': subject},
        ),
        subclass_3=dict(
            aci_class='vzRsSubjGraphAtt',
            aci_rn='rsSubjGraphAtt',
            module_object=SG,
            target_filter={'tnVnsAbsGraphName': SG},
        ),
    )

    aci.get_existing()

    if state == 'present':
        aci.payload(
            aci_class='vzRsSubjGraphAtt',
            class_config=dict(
                tnVnsAbsGraphName=SG,
            ),
        )
        aci.get_diff(aci_class='vzRsSubjGraphAtt'),
        aci.post_config()
    elif state == 'absent':
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()