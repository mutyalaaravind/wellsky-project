import { Button, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, useDisclosure } from "@chakra-ui/react"
import { Children, ReactNode } from "react"

export const ModalComponent = (props: { children: ReactNode, openModalText: string, modalTitle: string }) => {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return (
        <>
            <Button onClick={onOpen}>{props.openModalText}</Button>

            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>{props.modalTitle}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        {props.children}
                    </ModalBody>

                    {/* <ModalFooter>
                        <Button colorScheme='blue' mr={3} onClick={onClose}>
                            Submit
                        </Button>
                        <Button variant='ghost' onClick={onClose}>Cancel</Button>
                    </ModalFooter> */}
                </ModalContent>
            </Modal>
        </>
    )
}